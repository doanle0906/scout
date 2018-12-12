# -*- coding: utf-8 -*-
import logging
from datetime import datetime

LOG = logging.getLogger(__name__)

class MMEHandler(object):
    """Class to handle case submissions to MatchMaker Exchange"""

    def case_mme_update(self, case_obj, user_obj, mme_subm_obj):
        """Updates a case after a submission to MatchMaker Exchange

            Args:
                case_obj(dict): a scout case object
                user_obj(dict): a scout user object
                mme_subm_obj(dict): contains MME submission params and server response

        """
        created = None
        patient_ids = []
        updated = datetime.now()
        if 'mme_submission' in case_obj:
            created = case_obj['mme_submission']['created']
        else:
            created = updated
        patients_id = [ resp['patient_id'] for resp in mme_subm_obj.get('response')]

        mme_subm_obj = {
            'created' : created,
            'updated' : updated,
            'patient_id' : patients_id, # list of patients ids
            'subm_user' : user_obj['_id'] # submitting user
        }
        case_obj['mme_submission'] = mme_subm_obj
        updated_case = self.update_case(case_obj)

        return updated_case
