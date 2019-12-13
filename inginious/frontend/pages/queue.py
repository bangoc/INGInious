# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

""" Job queue status page """

from datetime import datetime, timedelta

from inginious.frontend.pages.utils import INGIniousAuthPage


class QueuePage(INGIniousAuthPage):
    """ Page allowing to view the status of the backend job queue """

    def GET_AUTH(self):
        """ GET request """
        if self.user_manager.user_is_superadmin():
            base_date = datetime.now()
            half_hour_date = base_date - timedelta(minutes=30)
            ten_min_date = base_date - timedelta(minutes=10)
            one_min_date = base_date - timedelta(minutes=1)
            one_day_date = base_date - timedelta(days=1)
            perhour_sub = {}
            subs = []
            subs_ten = []
            subs_min = []

            subs_one_day = list(self.database.submissions.find({
                "submitted_on": {'$gt': one_day_date}
            }))

            for sub in subs_one_day:
                hour = sub["submitted_on"].hour
                if hour in perhour_sub:
                    perhour_sub[hour] += 1
                else:
                    perhour_sub[hour] = 1
                if sub["submitted_on"] > half_hour_date:
                    subs.append(sub)
                if sub["submitted_on"] > ten_min_date:
                    subs_ten.append(sub)
                if sub["submitted_on"] > one_min_date:
                    subs_min.append(sub)

            return self.template_helper.get_renderer().queue(*self.submission_manager.get_job_queue_snapshot(),
                                                             datetime.fromtimestamp, len(subs), len(subs_ten),
                                                             len(subs_min),
                                                             perhour_sub)
        return self.template_helper.get_renderer().queue(*self.submission_manager.get_job_queue_snapshot(),
                                                         datetime.fromtimestamp, 0, 0, 0, {})
