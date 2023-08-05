Flask-Bundler
---

Flask-Bundler allows you to serve your project assets from Webpack directly,
allowing cache busting and easy deployment.

It uses Webpack's BundleTracker plugin to get information about the bundles
in your configuration and to serve them.

## Installation

You need to configure Webpack to output `webpack-stats.json`. For this, add
`webpack-bundle-tracker` as a Node dependency to your project and in your
`webpack.config.js` add:

``` javascript
const BundleTracker = require("webpack-bundle-tracker");
// ...
module.exports = {
    // ...
    plugins: [
        // ...
        new BundleTracker({
            filename: "./myapp/static/webpack-stats.json"
        }),
        // ...
    ],
    // ...
};
```

You can place the `webpack-stats.json` file anywhere in the application. By
default Flask-Bundler will check for `webpack-stats.json` inside the
application's static folder.

Afterwards, just initialize Flask-Bundler like you would with any extension.

### Normal initialization

``` python
from flask import Flask
from flask_bundler import Bundler

app = Flask(__name__)
# ...
bundler = Bundler(app)
```

### Application factory initialization

``` python
from flask import Flask
from flask_bundler import Bundler

bundler = Bundler()

def create_app():
    app = Flask(__name__)
    # ...
    bundler.init_app(app)
    # ...
    return app
```

## Bundler options

When initializing Bundler, you can specify a few options.

### `stats_file`

Path to the webpack-stats.json. Defaults to
`{app.static_folder}/webpack-stats.json.`

### `custom_renderers`

A dictionary of custom renderers. `str.format` will be called on the given
string with the public path of the asset as the only parameter. The default
renderers are `css` and `js`, but additional renderers can be passed if your
application contains other types of outputs.

### `strict`

If True, an error will be raised in exceptional situations. Otherwise, a warning
will be issued and the empty string will be returned for the bundle.

## License

&copy; Efe Mert Demir 2020. This software is licensed under the BSD license.
