import enum


class ResponseCode(enum.Enum):
    # ErrCredential error when executing repository query
    ErrCredential = "10001"
    # ErrMessageBodyIsEmpty message body is empty
    ErrMessageBodyIsEmpty = "10002"
    # ErrUserLimitted user is limited
    ErrUserLimitted = "10003"
    # ErrLineNotAssignedToYou line not assigned to you
    ErrLineNotAssignedToYou = "10004"
    # ErrRecipientsEmpty recipients is empty
    ErrRecipientsEmpty = "10005"
    # ErrCreditNotEnough credit not enough
    ErrCreditNotEnough = "10006"
    # ErrLineNotProfitForBulkSend line not profit for bulk send
    ErrLineNotProfitForBulkSend = "10007"
    # ErrLineDeactiveTemp line deactivated temporally
    ErrLineDeactiveTemp = "10008"
    # ErrMaximumRecipientExceeded maximum recipients number exceeded
    ErrMaximumRecipientExceeded = "10009"
    # ErrOperatorOffline operator is offline
    ErrOperatorOffline = "10010"
    # ErrNoPricing pricing not defined for user
    ErrNoPricing = "10011"
    # ErrTicketIsInvalid ticket is invalid
    ErrTicketIsInvalid = "10012"
    # ErrAccessDenied access denied
    ErrAccessDenied = "10013"
    # ErrPatternIsInvalid pattern is invalid
    ErrPatternIsInvalid = "10014"
    # ErrPatternParamettersInvalid pattern parameters is invalid
    ErrPatternParamettersInvalid = "10015"
    # ErrPatternIsInactive pattern is inactive
    ErrPatternIsInactive = "10016"
    # ErrPatternRecipientInvalid pattern recipient invalid
    ErrPatternRecipientInvalid = "10017"
    # ErrPatternUnAuthorizedSend unauthorized send with pattern
    ErrPatternUnAuthorizedSend = "10018"
    # ErrItsTimeToSleep send time is 8-23
    ErrItsTimeToSleep = "10019"
    # ErrCreditCardNotProvided credit card not provided
    ErrCreditCardNotProvided = "10020"
    # ErrDocumentsNotApproved one/all of users documents not approved
    ErrDocumentsNotApproved = "10021"
    # ErrInternal internal error
    ErrInternal = "10022"
    # ErrEntityNotFound internal error
    ErrEntityNotFound = "10023"
    # ErrForbidden internal error
    ErrForbidden = "10024"
    # ErrUnprocessableEntity inputs have some problems
    ErrUnprocessableEntity = "422"
    # ErrUnauthorized unauthorized
    ErrUnauthorized = "1401"
    # ErrKeyNotValid api key is not valid
    ErrKeyNotValid = "1402"
    # ErrKeyRevoked api key revoked
    ErrKeyRevoked = "1403"


class Error(Exception):
    """
    Error template
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

        super().__init__(str(message))


class HTTPError(Exception):
    pass

def parse_errors(response):
    if "error" in response.data:
        return Error(response.code, response.data["error"])
    return
