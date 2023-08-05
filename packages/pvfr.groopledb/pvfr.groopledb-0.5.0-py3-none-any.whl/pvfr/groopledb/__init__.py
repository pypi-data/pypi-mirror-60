'''
Copyright 2020 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----------------------------------------------------------------------------
Purpose: The groople module contains code to deal with the Groople Database
Filename: groople/__init__.py
Created Date: 2019-03-31
Author: Jacques Supcik
-----------------------------------------------------------------------------
'''

import datetime
import logging
import pathlib
import re

import records
import yaml

from .activity import Activity
from .category import Category
from .group import Group
from .organizer import Organizer
from .participant import Participant

try:
    # pylint: disable=unused-import,ungrouped-imports
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    # pylint: disable=unused-import,ungrouped-imports
    from yaml import Loader, Dumper

# pylint: disable=invalid-name

logger = logging.getLogger(__name__)

class Groople:

    def get_attribute_map(self, table):
        """ Returns the attribute map """
        attr_id = dict()
        rows = self.db.query(f'select * from _{table}')
        for r in rows:
            t = [k for (k, v) in self.config[table].items() if re.match(v, r.attribute_label)]
            if len(t) > 1:
                raise Exception(
                    f"Internal error : {len(t)} keys found for {r.attribute_label} ({t})")
            if len(t) == 1:
                attr_id[r.attribute_id] = t[0]
        return attr_id

    def __init__(self, db_url,
        year=datetime.datetime.now().year,
        config_file=pathlib.Path(pathlib.Path(__file__).parent, "config.yml")):

        self.db = records.Database(db_url)
        self.year = year
        self.config = yaml.load(open(config_file, 'r'), Loader=Loader)

        self.categories = None
        self.activities = None
        self.groups = None
        self.participants = None
        self.organizers = None
        self.activities_list = None
        
        self._read()

    def _read(self):
        self.categories = dict()
        self.activities = dict()
        self.groups = dict()
        self.participants = dict()
        self.organizers = dict()

        rows = self.db.query('select * from categories')
        for r in rows:
            c = Category(r.id, r.label, r.order_field, list())
            self.categories[r.id] = c

        rows = self.db.query('select * from activities')
        for r in rows:
            if r.enabled != 0 and r.activity_label != "DUMMY":
                a = Activity(
                    r.activity_id, r.activity_label, r.information, r.category_id, dict(), list()
                )
                self.activities[r.activity_id] = a
                c = self.categories.get(r.category_id, None)
                c.activities.append(a)

        aam = self.get_attribute_map('activity_attributes')
        uam = self.get_attribute_map('user_attributes')
        gam = self.get_attribute_map('group_attributes')

        rows = self.db.query('select * from activities_attributes')
        for r in rows:
            if r.activity_id in self.activities:
                a = self.activities[r.activity_id]
                key = aam.get(r.attribute_id, None)
                if key is not None:
                    a.attributes[key] = r.value

        rows = self.db.query('select * from activities_users_attributes_values')
        for r in rows:
            if r.activity_id in self.activities:
                a = self.activities[r.activity_id]
                key = uam.get(r.user_attribute_id, None)
                if key is not None:
                    a.attributes[key] = a.attributes.get(
                        key, list()) + [r.attribute_value]

        rows = self.db.query('select * from groups')
        for r in rows:
            if r.group_active == 'T':
                g = Group(r.group_id, r.group_label, r.maxQuota)
                self.groups[r.group_id] = g
                if r.activity_id in self.activities:
                    self.activities[r.activity_id].groups.append(g)

        rows = self.db.query('select * from groups_attributes')
        for r in rows:
            if r.group_id in self.groups:
                g = self.groups[r.group_id]
                key = gam.get(r.attribute_id, None)
                if key is not None:
                    g.attributes[key] = r.value

        # Fix/complete groups
        for g in self.groups.values():
            g.sanitize(self.year)

        # Fix/complete activities and sort groups
        for a in self.activities.values():
            a.sanitize()
            a.sort_groups()

        # sort all activities
        for c in self.categories.values():
            c.sort_activities()

        # Extract Organizers

        for a in self.activities.values():
            o = Organizer(
                id=-1,
                name=a.attributes['organizer_name'],
                address=a.attributes.get('organizer_address', None),
                phone=a.attributes.get('organizer_phone', None),
                email=a.attributes.get('organizer_email', None),
                presence_list_to=a.attributes.get(
                    'participants_list_to_name', None),
                presence_list_to_email=a.attributes.get(
                    'participants_list_to_email', None),
            )
            o.fix_id()
            o.email_list = a.orga_email_list
            o.email_presence_list = a.orga_email_list_participants

            if o.id in self.organizers:
                o = self.organizers[o.id]
            else:
                self.organizers[o.id] = o
            o.activities.add(a.id)
            a.organizer_id = o.id

        # FETCH PARTICIPANTS

        rows = self.db.query('select * from users')
        for r in rows:
            p = Participant(
                r.user_id,
                username=r.username,
                firstname=r.firstname,
                lastname=r.lastname,
                email=r.email,
            )
            self.participants[p.id] = p

        rows = self.db.query('select * from users_attributes')
        for r in rows:
            if r.user_id not in self.participants:
                logger.warning(f"User {r.user_id} not found")
                continue
            p = self.participants[r.user_id]
            key = uam.get(r.attribute_id, None)
            if key is not None:
                p.attributes[key] = r.value

        rows = self.db.query('select * from attributions')
        for r in rows:
            if r.user_id not in self.participants:
                logger.warning(f"User {r.user_id} not found")
                continue
            if r.group_id not in self.groups:
                logger.warning(f"Group {r.group_id} not found")
                continue
            p = self.participants[r.user_id]
            g = self.groups[r.group_id]
            p.groups.add(g.id)
            g.participants.add(p.id)

        self.activities_list = sorted(self.categories.values(), key=lambda x: x.order)


    def activities_to_agenda(self):
        """ Returns an agenda from the activities """
        dow = ["lundi", "mardi", "mercredi", "jeudi",
            "vendredi", "samedi", "dimanche"]
        mths = ["janvier", "février", "mars", "avril", "mai", "juin",
                "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        allpass = list()
        agenda = dict()
        for c in self.categories:
            for a in c.activities:
                if a.attributes.get("all_pass", False):
                    allpass.append(a)
                    continue
                gi = 0
                for g in a.groups:
                    gi += 1
                    for d in g.days:
                        if d["day"] is None or d["month"] is None:
                            print(f"Ignoring {a.name}")
                            continue
                        key = (d["day"], d["month"])
                        value = {
                            'activity': a,
                            'schedule': d['schedule'],
                            'order': d['order'],
                            'index': gi,
                            'len': len(a.groups)
                        }

                        sc = d['schedule']
                        m = re.search(
                            r'(\d{1,2})[h:.](\d{1,2}).*?(\d{1,2})[h:.](\d{1,2})', sc)
                        if m:
                            value['schedule_2'] = "{0:02d}h{1:02d} - {2:02d}h{3:02d}".format(
                                int(m.group(1)),
                                int(m.group(2)),
                                int(m.group(3)),
                                int(m.group(4)),
                            )
                        else:
                            value['schedule_2'] = sc

                        if key not in agenda:
                            agenda[key] = list()

                        if value not in agenda[key]:
                            agenda[key].append(value)

        res = list()
        for i in sorted(agenda.keys(), key=lambda x: x[0] + x[1] * 32):
            d = datetime.date(self.year, int(i[1]), int(i[0]))
            res.append({
                "id": i,
                "date": f"{dow[d.isoweekday()-1]} {d.day} {mths[d.month-1]}",
                "activities": sorted(agenda[i], key=lambda x: x['order']),
            })

        for i in res:
            print(f"Date : {i['date']}")
            for j in i['activities']:
                print(
                    f"{j['activity'].name} {j['index']}/{j['len']} -> {j['schedule']}")

        return res
