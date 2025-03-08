DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'card',    
    'visa',
    'mastercard',
    'amex',
    'discover',
]

# Mapping of transaction states to Fygaro payment statuses.
SUCCESS_CODE_MAPPING = {
    'pending': ['pending auth'],
    'done': ['3',3],
    'cancel': ['0',0],
    'error': ['2',2],
}


