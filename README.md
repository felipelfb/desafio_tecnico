A single endpoint application to access a weather summary of a specific city.

To launch the local server in development mode, run the following commands (on a UNIX based OS):

```
export FLASK_APP=weather.py
export FLASK_ENV=development
run flask
```

The single local endpoint is http://127.0.0.1:5000/weather/ and it requires three query parameters:

> * city: ID of the specific city
> * date_begin: initial date on the YYYYMMDD format
> * date_finish end date on the YYYYMMDD format

For example, to get data from São Paulo (ID 3477) from 19/06/2019 until 23/06/2019, the URL would be:

> http://127.0.0.1:5000/weather/?city=3477&date_begin=20190619&date_finish=20190623

It is important to note that both date_begin and date_finish have to be equal or greater than the current date, but not greater than 7 days. Also, date_finish has to be greater or equal to date_begin.

The response is a JSON in the following format:

```
{
  "min_temp_date": "2019-06-21",
  "min_temp": 14,
  "max_temp_date": "2019-06-19",
  "max_temp": 26,
  "most_probable_rain_date":
  "2019-06-20",
  "rain_amount": 5
 }
 ```
 
