# GenXData
A Complete synthetic data framework for generating realistic data for your applications.

## Getting Started
**Step 1**: Install dependencies
```bash
pip install -r requirements.txt
```

**Step 2**: Create a configuration file. You can copy `examples/config.json.example` to `examples/config.json`, or create your own config (refer to examples folder for more info).

**Step 3**: Run the script with your configuration:
```bash
python data_generator.py ./examples/config.json
```

For verbose output and debugging information, use the debug flag:
```bash
python data_generator.py ./examples/config.json --debug
```


### Docker
Note: A React frontend app is present inside the [frontend](frontend) directory, built solely to quickly bootstrap the config, and to showcase the capabilities of the tool for demo showcase.

The docker image will serve the frontend, a fast api server, to generate config or data

#### Build the image
```bash
docker build -t genxdata .
```

#### Run the container
```bash
docker run -it genxdata
```

#### Or Pull the image
```bash
docker pull tosifkhan/genxdata:latest
```

then run the container

```bash
docker run -p 8000:8000 -it tosifkhan/genxdata:latest
```

visit the frontend at `http://localhost:8000`
see the api server docs at `http://localhost:8000/docs`


## Key Concepts

### Strategies (`strategy`)
A strategy defines how the data is going to be generated for a column.

Strategies are the core of the framework. They are the building blocks of the data generation pipeline. another way to think about it is that strategies are the functions that are used to generate the data. they are the lower-level apis that are used to generate the data.

### Generators (`generator`)
A generator is a wrapper around a collection of strategies that are used to generate the data for a column.

Generators are the higher-level apis, an abstraction to hide the parameters of strategies. and generating data seemlessly.

for example, Person Name can be a generator that is a wrapper around the [Random Name Strategy](./strategies/random_name_strategy.py)

or a Date of Birth can be a generator that is a wrapper around the [Date Generator Strategy](./strategies/date_generator_strategy.py) that is used to generate this kind of data.

and so on, There can be 100s of generators

## About the tool

The `main.py` reads a config file in `yaml` format and applies data generation strategies based on the config file to the columns. The script uses various data generation strategies such as regular expression, series, random names, and distribution-based data generation. It is capable of generating data independently or dependent on other columns for each column.


## Available Strategies

The following strategies are available:

1. **DATE_GENERATOR_STRATEGY**: Generate date values within a range
2. **DELETE_STRATEGY**: Delete values from a column
3. **DISTRIBUTED_NUMBER_RANGE_STRATEGY**: Generate numbers with custom distributions
4. **DISTRIBUTED_CHOICE_STRATEGY**: Generate categorical data with custom distributions
5. **RANDOM_NUMBER_RANGE_STRATEGY**: Generate random numbers within a range
6. **RANDOM_NAME_STRATEGY**: Generate random names
7. **PATTERN_STRATEGY**: Generate data matching a regex or pattern
8. **TIME_RANGE_STRATEGY**: Generate time values within a range
9. **REPLACEMENT_STRATEGY**: Replace specific values
10. **SERIES_STRATEGY**: Generate a series of values
11. **DISTRIBUTED_DATE_STRATEGY**: Generate dates with custom distributions
12. **CONCAT_STRATEGY**: Concatenate values from other columns

Although there could be more strategies, but the above ones can be the foundation for most of the data generation needs. and above that you can use generators to create more complex data generation logic.

### Performance Monitoring
You can generate a performance report for your data generation by using the `--perf` flag:

```bash
python main.py ./examples/config.yaml --perf
```
This will show detailed timing information for each operation, helping you identify bottlenecks in your data generation pipeline. The report includes:
- Time spent on each column/strategy
- Average execution time
- Rows processed per second


## Output Formats
The data generator supports multiple output formats. You can specify one or more file writers in your configuration file:

### Available File Writers
- CSV
- Excel
- JSON
- Parquet
- SQLite
- HTML
- Feather

You can specify multiple writers to output the same data in different formats simultaneously. See `examples` for a complete example.

## YAML Configuration Support

The data generator now supports a more readable YAML configuration, see `examples/all_example.yaml` for a complete example.


Consider dropping a star ⭐️ if you like the project.
Or I Would glad to hear any questions, feedback, feature requests or bug reports.
[twitter](https://x.com/@beingkarnage)
[linkedin](https://www.linkedin.com/in/tosifkhan99/)
[khantosif94@gmail.com](mailto:khantosif94@gmail.com)

