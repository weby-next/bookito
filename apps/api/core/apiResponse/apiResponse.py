from rest_framework.response import Response


class ApiResponse:

    @staticmethod
    def success(message="Success", data=None, status_code=200):
        return Response(
            {
                "success": True,
                "message": message,
                "data": {} if data is None else data,
            },
            status=status_code,
        )

    @staticmethod
    def error(
        code="INTERNAL_ERROR",
        message="An error occurred.",
        fields=None,
        status_code=400,
    ):
        response_data = {
            "code": code,
            "message": message,
        }

        if fields is not None:
            response_data["fields"] = fields

        return Response(response_data, status=status_code)
