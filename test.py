import ibm_db

conn = ibm_db.connect("DATABASE=name;"
                      "HOSTNAME=hostname;"
                      "PORT=port;"
                      "PROTOCOL=TCPIP;"
                      "UID=user;"
                      "PWD=password;"
                      , ""
                      , "")
stmt = ibm_db.exec_immediate(conn, "SELECT * FROM table")
result = ibm_db.fetch_both(stmt)
