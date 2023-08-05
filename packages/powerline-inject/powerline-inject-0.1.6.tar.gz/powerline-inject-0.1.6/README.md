# powerline-inject 

[![pypi](http://img.shields.io/pypi/v/powerline-inject.png)](https://pypi.python.org/pypi/powerline-inject)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/powerline-inject.svg)](https://pypi.python.org/pypi/powerline-inject/)
[![License](https://img.shields.io/pypi/l/powerline-inject.svg)](https://pypi.python.org/pypi/powerline-inject/)

`powerline-inject` is a [Powerline](https://github.com/powerline/powerline) status segment addon for showing ENV with extra knobs.

This can be natively done with `powerline.segments.common.env.environment` if knobs aren't needed:

```json
{
	"segments":
	{
		"left":
		[
			{ "function":
				"powerline.segments.common.env.environment",
				"name": "aws",
				"priority": 20,
				"before": "⩜ ",
				"args": {
					"variable": "SOME_ENV"
				}
			}
		]
	}
}
```

Couple knobs featured that `powerline-inject` has are:

1. The ability to toggle on or off the powerline-inject segment using an environment variable which can easily be mapped to a function in your `~/.bash_profile`.
2. The ability to show only a symbol when the variables holds value. (SECRET KEYS, TOKENS, etc.)
3. Multiple different highlighter profiles for your ENV lists.

The screenshot below demonstrates this functionality:

[![screenshot](usage_screenshot.png)](https://pypi.org/project/powerline-inject/)

## Installation

1. **Add the Python package**.  powerline-inject is available on pypi so you can install it with pip:

```bash
pip install --user powerline-inject
```

2. **Create a user configuration directory**. 

Once powerline-inject has been installed, we'll need to add it to our powerline shell's theme and colorscheme. 

Alter your powerline user config: 

If you don't already have a `~/.config/powerline/` folder, create it. Next we'll be copying some of the default powerline configs into this location. Find where powerline is installed by using `pip show powerline-status | grep 'Location'`, then navigate to the `config_files/` folder there. We'll be copying `config.json`, `themes/shell/default.json`, and `colorschemes/shell/default.json` to our `~/.config/powerline/` folder, adding the necessary folders to match that original file structure (i.e. adding the `themes/` and `colorschemes/` folders, etc.

3. **Add powerline-inject to your user config**. 

Within our user config, we'll need to add the powerline-inject segment to our shell by adding the following lines to our `~/.config/powerline/themes/shell/default.json`:

```json
    {
	    "function": "powerline_inject.context",
	    "priority": 30,
	    "args": {
			"show_env": true,
			"env_list": ["AWS_PROFILE", "TOKEN_X"]
		}
    }
```

Next we'll add the highlighting colors we'll use to our `~/.config/powerline/colorschemes/shell/default.json`:

```json
    {
	    "name": "Default",
	    "groups": {
			"powerline_inject": { "fg": "white", "bg": "red", "attrs": [] },
			"powerline_inject_bold": { "fg": "white", "bg": "brightred", "attrs": [] },
	    }
    }
```

4. You will need to reload powerline with `powerline-daemon --replace` to load the new settings. That's it!

5. (Optional) By default powerline-inject will render the environment variable if `RENDER_POWERLINE_INJECTS` is either set to `YES` or is not set at all. Rather than setting this variable manually, you can create a simple `powerline-inject-toggle` function by placing the following in your `~/.bash_profile`:

```bash
        function powerline-injects-toggle() {
            if [[ $RENDER_POWERLINE_INJECTS = "NO" ]]; then
                export RENDER_POWERLINE_INJECTS="YES"
            else
                export RENDER_POWERLINE_INJECTS="NO"
            fi
        }
```

## Confidential ENV use

You may find you want to know when you have **SECRETS** loaded into your **ENVIRONMENT**. This will show only a symbol `⩜` when the `SECRET_TOKEN` or `AWS_PROFILE` is loaded.

```json
	{
		"function": "powerline_inject.context",
		"priority": 30,
		"args": {
			"show_env": false,
			"env_list": ["SECRET_TOKEN", "AWS_PROFILE"],
			"before": "⩜ "
		}
	},
```

You can further add a second call to `powerline_inject.context` with a different `before` symbol and/or `env_highlighter` in args like the `powerline_inject_bold` defined above.

```json
	{
		"function": "powerline_inject.context",
		"priority": 30,
		"name": "second_injection",
		"args": {
			"show_env": false,
			"env_list": ["SECRET_TOKEN", "AWS_PROFILE"],
			"env_highlighter": "powerline_inject_bold"
		}
	},
```

## Used with `PROMPT_COMMAND` for ENV refresh

You may want to use this with a PROMPT COMMAND that updates the ENVs being checked everytime. As an example `aws-test-authentication` sets `AWS_EPOCH` and `AWS_PROFILE`.

Put this in your `~/.bash_profile`

```bash
export PROMPT_COMMAND="eval \$(aws-test-authentication); $PROMPT_COMMAND"
```

You're all set up! Happy coding!

## License

Licensed under the [Apache License 2.0](LICENSE).  
Original fork is at https://github.com/zcmarine/powerkube.
