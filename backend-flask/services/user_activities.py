from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

class UserActivities:
    @xray_recorder.capture('user_activities')
    def run(user_handle):
        model = {
            'errors': None,
            'data': None
        }

        now = datetime.now(timezone.utc).astimezone()

        try:
            if user_handle == None or len(user_handle) < 1:
                model['errors'] = ['blank_user_handle']
            else:
                with xray_recorder.in_subsegment('mock-data'):
                    # Mock data generation
                    results = [{
                        'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
                        'handle': 'Grey Alora',
                        'message': 'Cloud is fun!',
                        'created_at': (now - timedelta(days=1)).isoformat(),
                        'expires_at': (now + timedelta(days=31)).isoformat()
                    }]
                    model['data'] = results

                    # Add metadata
                    xray_recorder.current_subsegment().put_metadata(
                        'key', {
                            "now": now.isoformat(),
                            "results-size": len(model['data'])
                        },
                        'namespace'
                    )

        except Exception as e:
            # Handle exceptions and add error to the segment
            xray_recorder.current_segment().put_error(
                'Error', 'Exception', str(e)
            )
            model['errors'] = [str(e)]

        return model
