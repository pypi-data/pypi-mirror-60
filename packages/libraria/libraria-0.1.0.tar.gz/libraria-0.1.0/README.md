# Libraria

A python library used for searching libraries for books. Currently, only the San Francisco
Bay Area libraries are supported.

# Upcoming Features

- More comprehensive tests
- implement support for using [advanced search]("https://smplibrary.bibliocommons.com/search")

### Installing

```
pip3 install libraria
libraria 'byzantine empire'
S76C2550363,The Culture of the Byzantine Empire,BK,['9781508150015', '150815001X', '9781508150060', '1508150060']
S76C1793574,The Byzantine Empire,BK,['9781410305862', '1410305864']
S76C1672035,Daily Life in the Byzantine Empire,BK,['9780313324376', '0313324379']
S76C2047443,History of the Byzantine Empire,EBOOK,[]
S76C1340752,The Byzantine Empire,BK,['9780684166520', '0684166526']
S76C2034317,The End of the Byzantine Empire,EBOOK,[]
S76C1443729,The Byzantine Empire,BK,['9781560063070', '1560063076']
S76C1718171,The Byzantine Empire,BK,['9781590188378', '1590188373']
S76C2636299,The Byzantine Empire,BK,['9781680487800', '1680487809', '9781680488616', '1680488619']
S76C1618227,The Byzantine Empire,BK,['9780761414957', '0761414959']
```


## Running the tests

To execute tests, run `poetry run pytest tests`

## License

MIT License
