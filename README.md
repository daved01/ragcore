# Document Query Tool

There is a command line option and a UI option. To use the latter, run `uvicorn fastapi_app:app --reload`.

To run the command line option, run `python -m docucite.cli`.

## Getting started

## App structure

The app is structured into the layers `api`, `app`, `services`, and `model`.

The structure is

```
├── docs
├── docucite
├── notes
├── static
├── tests
    └──

```

## Development

Install dependencies with `pip install -r requirements_dev.txt`.

All code in the main folder `docucite` must be tested and of high quality. The folder

## Testing

## Ideas

- Build query app to use  the openai API
- Swap out API with local integration (run on tinygrad?)
