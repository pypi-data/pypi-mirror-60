# Canonical Phone
## Purpose
Convert given phone number into a string with hiphenated phone number with country code.
Default is assumed to be Indonesian number.

## How to use?
```python
from canonical_phone.phone import canonical_number
phone_no = canonical_number(phone) # If invalid, returns False
if not phone_no:
    raise Exception("invalid phone number")
```