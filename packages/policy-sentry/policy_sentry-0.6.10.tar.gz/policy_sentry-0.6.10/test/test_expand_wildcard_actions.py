from policy_sentry.analysis.analyze import determine_actions_to_expand
from policy_sentry.shared.database import connect_db
from policy_sentry.shared.constants import DATABASE_FILE_PATH
import unittest

db_session = connect_db(DATABASE_FILE_PATH)


class ExpandWildcardActionsTestCase(unittest.TestCase):
    def test_determine_actions_to_expand(self):
        """
        test_determine_actions_to_expand: provide expanded list of actions, like ecr:*
        :return:
        """
        action_list = [
            "ecr:*"
        ]
        self.maxDiff = None
        desired_result = [
            'ecr:batchchecklayeravailability',
            'ecr:deleterepository',
            'ecr:getauthorizationtoken',
            'ecr:getlifecyclepolicy',
            'ecr:deleterepositorypolicy',
            'ecr:getdownloadurlforlayer',
            'ecr:untagresource',
            'ecr:startlifecyclepolicypreview',
            'ecr:listimages',
            'ecr:completelayerupload',
            'ecr:tagresource',
            'ecr:getrepositorypolicy',
            'ecr:initiatelayerupload',
            'ecr:setrepositorypolicy',
            'ecr:startimagescan',
            'ecr:putlifecyclepolicy',
            'ecr:deletelifecyclepolicy',
            'ecr:describeimages',
            'ecr:describeimagescanfindings',
            'ecr:createrepository',
            'ecr:describerepositories',
            'ecr:batchgetimage',
            'ecr:putimage',
            'ecr:putimagescanningconfiguration',
            'ecr:putimagetagmutability',
            'ecr:getlifecyclepolicypreview',
            'ecr:listtagsforresource',
            'ecr:uploadlayerpart',
            'ecr:batchdeleteimage'
        ]
        print(determine_actions_to_expand(db_session, action_list))
        self.maxDiff = None
        self.assertListEqual(sorted(determine_actions_to_expand(db_session, action_list)), sorted(desired_result))
