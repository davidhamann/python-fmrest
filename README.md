# python-fmrest

Working on the first bits. Proper README coming as soon as it's usable.

- [x] auth: login, logout
- [x] record get
- [x] record create
- [x] record delete
- [ ] record edit
- [ ] records get
- [ ] find
- [ ] globals

---

Sample usage:

```
# create server instance
fms = fmrest.Server('https://server-ip',
                    user='admin',
                    password='admin',
                    database='fmwrapper',
                    layout='Contacts'
                   )

# login
fms.login()

# specify which portals to fetch
portals = [{'name': 'notes'}]

# fetch record
record = fms.get_record(1, portals)

# access fields
record.name
```
