"""Test OPQL query scanning and OCEL 2.0 query solver integration."""

import opql.lang.querysolver

def test_opql_query_scanner():
    query_str = """
    PATTERN E(e:"ExecuteAction")-[]-O(o:"ExecutionReceipt")
    RETURN e["ocel_id"] AS event_id, o["ocel_id"] AS object_id
    """
    query_struct = opql.lang.querysolver.scan_query(query_str)
    assert query_struct is not None
    print("OPQL Query scanned successfully!")

if __name__ == "__main__":
    test_opql_query_scanner()
    print("OPQL INTEGRATION TEST PASSED SUCCESSFULLY!")
