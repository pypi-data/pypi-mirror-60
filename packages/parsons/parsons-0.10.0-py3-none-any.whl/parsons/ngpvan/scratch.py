from parsons import Zoom

import logging
parsons_logger = logging.getLogger('parsons')
parsons_logger.setLevel('DEBUG')

api_key = 'q5E1Lyx1T1enFlvfWpJ8eg'
api_secret = 'jmjdRv46WTJmMFQ6MwQdLAKtllc7nemh1baL'

z = Zoom(api_key=api_key, api_secret=api_secret)
#y = z.get_users()

usr = 'HVepXoOKQMGokpyIWbLlGg'

y = z.get_webinars(usr)

p = z.get_webinar_participants('250688413')

