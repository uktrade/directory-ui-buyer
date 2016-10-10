Simple form to collect some data on people/companies that are interested in being included in the directory.

# Front End

## Dependencies

You will need to have [SASS](http://sass-lang.com/) installed and available in your PATH
You will need [node](https://nodejs.org/en/download/) (and npm) installed

## Setup

Install the node deps:

```bash
npm install
```

Then build the sass:

```bash
npm run sass-dev
```

## Dev

To enable easy development, you can have sass watch the scss file for changes.

```bash
npm run sass-watch
```

This will cause sass to rebuld the css files when the scss file changes.


# Terms info

(Please do not delete this section)

We changed the wording of the terms, which means some people could have agreed to different terms.

The original terms were tagged up to 1.4 and the new terms were introduced with tag 1.5 on 28/07/2016


# Session

We use signed cookies as the session backend. The reason for this is to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.
