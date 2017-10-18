#
# using this to prevent the file from running if someone decides
# to "import" this into their program
#
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Audit of customer's EM7 MIB database ")
    parser.add_argument("--apiUser",  action="store", dest="userName",  default="root", help="User with sudo privs")
    parser.add_argument("--Server",   action="store", dest="Server_id", default="None", help="Commas separated list of servers")
    parser.add_argument("--CustId",   action="store", dest="cust_id",   default="None", help="Unique customer stack id")
    parser.add_argument("--FeatId",   action="store", dest="feat_id",   default="None", help="Feature")
    parser.add_argument("--FuncId",   action="store", dest="func_id",   default="None", help="Function")
    parser.add_argument("--Audit",    action="store", dest="auditid",   default="None", help="Audit ID number")
    parser.add_argument("--DBPort",   action="store", dest="dbPort",    default="None", help="EM7 Database port")
    parser.add_argument("--DBServer", action="store", dest="dbServer",  default="None", help="EM7 Database Server")
    parser.add_argument("--DBType",   action="store", dest="dbType",    default="None", help="EM7 Database type")
    parser.add_argument("--DBUser",   action="store", dest="dbUser",    default="None", help="EM7 Database user")

    parser.add_argument("--SummaryFile", action="store", dest="sumFile", default="None", help="File to store audit Summary information")
    parser.add_argument("--DetailFile",  action="store", dest="detFile", default="None", help="File to store audit Detail information")

    args = parser.parse_args()

    print args

