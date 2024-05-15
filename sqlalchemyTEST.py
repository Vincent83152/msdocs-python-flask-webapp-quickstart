# -*- coding: utf-8 -*-
from sqlalchemyDemo import Test, create_session
from pprint import pprint

session = create_session()
# res = session.query(Test).filter(Test.records["性別"] == "女").all()

res = session.query(Test).first()

print(str(res.records))
# for row in res:
#     print(row.id, end=" ")
#     print(row.records["Seq"], end=" ")
#     print(row.records["性別"], end=" ")
#     print(row.records["級別"])


# session.add(Test(records='{}'))

session.commit()
session.close()