from .basestore import *

class ChallengeUpdateFailure(CatalogUpdateFailure):
    pass

class ChallengeStore(BaseStore):
    """Create and manage challenge problem metadata
    Records are linked with samples via challenge-specific uuid"""

    def __init__(self, mongodb, config, session=None):
        super(ChallengeStore, self).__init__(mongodb, config, session)
        coll = config['collections']['challenges']
        if config['debug']:
            coll = '_'.join([coll, str(time_stamp(rounded=True))])
        self.name = coll
        self.coll = self.db[coll]
        self._post_init()

    def update_properties(self, dbrec):
        ts = current_time()
        properties = dbrec.get('properties', {})
        properties['created_date'] = properties.get('created_date', ts)
        if properties.get('modified_date', ts) >= ts:
            properties['modified_date'] = ts
        properties['revision'] = properties.get('revision', 0) + 1
        dbrec['properties'] = data_merge(dbrec['properties'], properties)
        return dbrec

    def create_update_challenge(self, challenge, parents=None, uuid=None):
        ts = current_time()
        challenge_uuid = None
        # Absolutely must
        if 'challenge_problem' not in challenge:
            raise ChallengeUpdateFailure(
                '"challenge_problem" missing from record')
        # Add UUID if it does not exist (record is likely new)
        if 'uuid' not in challenge:
            challenge_uuid = catalog_uuid(challenge['challenge_problem'])
            challenge['uuid'] = challenge_uuid
        # this list maintains the inheritance relationship
        # challenge_problems currently have no parent but we include
        # an affordance for one in the data model
        if parents is None:
            parents = []
        if isinstance(parents, str):
            parents = [parents]
        challenge['child_of'] = parents

        # Filter keys we manage elsewhere or that are otherwise uninformative
        for k in ['samples', 'experiment_id', 'experiment_reference', 'lab']:
            try:
                challenge.pop(k)
            except KeyError:
                pass

        # Try to fetch the existing record
        dbrec = self.coll.find_one({'uuid': challenge_uuid})
        if dbrec is None:
            dbrec = challenge
            challenge['properties'] = {'created_date': ts,
                                    'modified_date': ts,
                                    'revision': 0}
            try:
                result = self.coll.insert_one(challenge)
                return self.coll.find_one({'_id': result.inserted_id})
            except Exception as exc:
                raise ChallengeUpdateFailure(
                    'Failed to create challenge problem record', exc)
        else:
        # Update the fields content of the record using a rightward merge,
        # then update the updated and revision properties, then write the
        # record (and eventually its diff) to the catalog
            dbrec = self.update_properties(dbrec)
            dbrec_core = copy.deepcopy(dbrec)
            dbrec_props = dbrec_core.pop('properties')
            challenge_core = copy.deepcopy(challenge)
            # merge in fields data
            dbrec_core_1 = copy.deepcopy(dbrec_core)
            dbrec_core_1.pop('_id')
            new_rec, jdiff = data_merge_diff(dbrec_core, challenge_core)
            # Store diff in our append-only updates log
            self.log(challenge_uuid, jdiff)
            new_rec['properties'] = dbrec_props
            try:
                uprec = self.coll.find_one_and_replace(
                    {'_id': new_rec['_id']}, new_rec,
                    return_document=ReturnDocument.AFTER)
                return uprec
            except Exception as exc:
                raise ChallengeUpdateFailure(
                    'Failed to update existing challenge problem', exc)

    def delete_record(self, challenge_id):
        '''Delete record by challenge.id'''
        try:
            return self.coll.remove({'id': challenge_id})
        except Exception as exc:
            raise ChallengeUpdateFailure(
                'Failed to delete challenge {}'.format(challenge_id), exc)

