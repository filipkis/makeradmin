#!/usr/bin/env python3
import servicebase_python.service
import json
from pprint import pprint

gateway = servicebase_python.service.gateway_from_envfile(".env")

"labaccess"
"special_labaccess"
"membership"


def delete_all_spans(member_id):
    response = gateway.get("membership/span")
    print("list", response.status_code)
    spans = json.loads(response.content.decode())['data']
    for span in spans:
        response = gateway.delete(f"membership/span/{span['span_id']}")
        print("delete", response.status_code)
        

def create_span(member_id, startdate, enddate, span_type, creation_reason=None):
    payload = dict(
        member_id=member_id,
        startdate=startdate,
        enddate=enddate,
        span_type=span_type,
        creation_reason=creation_reason,
    )

    response = gateway.post("membership/span", payload=payload)
    print("create", response.status_code)
    pprint(json.loads(response.content.decode()))


member_id = 76
    
delete_all_spans(member_id)

create_span(member_id, "2016-05-20", "2016-06-21", "labaccess")
create_span(member_id, "2016-06-21", "2016-07-21", "labaccess")

create_span(member_id, "2018-05-10", "2018-07-10", "labaccess")
create_span(member_id, "2018-07-11", "2018-11-11", "labaccess")

create_span(member_id, "2018-05-20", "2019-05-20", "membership")

create_span(member_id, "2018-05-10", "2019-05-10", "special_labaccess")

# insert into membership_group_permissions (id, group_id,
# permission_id) values ( 1, 1, 1), ( 2, 1, 2),( 3, 1, 3), ( 4, 1, 4),
# ( 5, 1, 5), ( 6, 1, 6), ( 7, 1, 7), ( 8, 1, 8), ( 9, 1, 9), (10, 1,
# 10), (11, 1, 11), (12, 1, 12), (13, 1, 13), (14, 1, 14), (15, 1,
# 15), (16, 1, 16), (17, 1, 17), (18, 1, 18), (19, 1, 19), (20, 1,
# 20), (21, 1, 21), (22, 1, 22), (23, 1, 23), (24, 1, 24);

