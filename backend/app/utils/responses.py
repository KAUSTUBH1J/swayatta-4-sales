def Response(
    message, 
    status_code, 
    json_data=None
):
    try:
        return {
            "status_code": status_code,
            "message": message,
            "data": json_data,
        }
    except Exception as e:
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": f"Response Failed: {str(e)}",
            "data": None,
        }