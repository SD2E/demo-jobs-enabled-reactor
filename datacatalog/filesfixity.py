from .basestore import *
import datetime
class FileFixtyUpdateFailure(CatalogUpdateFailure):
    pass

class FileFixityStore(BaseStore):
    """Create and manage fixity records
    Records are linked with FilesMetadataStore via same uuid for a given filename"""
    def __init__(self, mongodb, config):
        super(FileFixityStore, self).__init__(mongodb, config)
        coll = config['collections']['fixity']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()

    def checkfile(self, filepath):
        '''Check if a filepath exists and is believed by the OS to be a file'''
        full_path = self.abspath(filepath)
        if os.path.isfile(full_path) and os.path.exists(full_path):
            return True
        else:
            return False

    def get_fixity_template(self, filename):
        t = {'file_created': None,
             'file_modified': None,
             'created_date': None,
             'modified_date': None,
             'file_type': None,
             'size': None,
             'checksum': None,
             'lab': labname_from_path(filename)}
        return t

    def get_fixity_properties(self, filename, timestamp=None, properties={}):
        """Learn or update the properties of filename
        Params:
            filename (str): a datafile.filename, which is a relative path
        Returns:
            dict containing a datafiles.properties
        """
        absfilename = self.abspath(filename)
        orig_properties = copy.deepcopy(properties)
        try:
            mtime = get_modification_date(absfilename)
            properties['file_modified'] = mtime
            # First time
            if 'file_created' in properties:
                if not isinstance(properties.get('file_created', None), datetime.datetime):
                    properties['file_created']=mtime
            else:
                properties['file_created']=mtime
        except Exception:
            pass
        # file type
        try:
            ftype = get_filetype(absfilename)
            properties['file_type'] = ftype
        except Exception:
            pass
        # checksum
        try:
            cksum = compute_checksum(absfilename)
            properties['checksum'] = cksum
        except Exception:
            pass
        # size in bytes
        try:
            size = get_size_in_bytes(absfilename)
            properties['size'] = size
        except Exception:
            pass
        return properties

    def create_update_file(self, filename):
        """Create a DataFile record from a filename resolving to a physical path
        Parameters:
            filename (str) is the filename relative to DataCatalog.root
        Returns:
            dict-like PyMongo record
        """
        filename = self.normalize(filename)
        file_uuid = catalog_uuid(filename)
        ts = current_time()

        # Exists?
        filerec = self.coll.find_one({'filename': filename})
        if filerec is None:
            filerec = {'filename': filename,
                       'uuid': file_uuid}
            # get template
            props = self.get_fixity_template(filename)
            # update with file fixity properties
            props = self.get_fixity_properties(filename, props)
            # update record-level properties
            props['created_date'] = ts
            props['modified_date'] = ts
            props['revision'] = 0
            filerec['properties'] = props
            try:
                result = self.coll.insert_one(filerec)
                return self.coll.find_one({'_id': result.inserted_id})
            except Exception:
                raise FileFixtyUpdateFailure(
                    'Failed to create file metadata')
        else:
            # Keep to use when computing difflog
            ofilerec = copy.deepcopy(filerec)
            # force UUID (this is a transparent migration to binary UUIDs)
            filerec['uuid'] = file_uuid
            # update an existing record's physical properties
            props = self.get_fixity_properties(
                filename, properties=filerec.get('properties', {}))
            # update database record properties
            props['modified_date'] = ts
            if not 'created_date' in props:
                props['created_date'] = ts
            props['revision'] = props.get('revision', 0) + 1
            filerec['properties'] = data_merge(ofilerec['properties'], props)
            jdiff = json_diff(ofilerec, filerec)
            self.log(file_uuid, jdiff)
            try:
                uprec = self.coll.find_one_and_replace(
                    {'_id': filerec['_id']}, filerec,
                    return_document=ReturnDocument.AFTER)
                return uprec
            except Exception as exc:
                raise FileFixtyUpdateFailure(
                    'Failed to update existing file', exc)
