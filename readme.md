# "BrandMeister Event Feed"

Home Assistant component for accessing feed of BrandMeister events.


## Installation

Clone this repository into `custom_components` directory.


## Configuration

Currently, the configuration can only be done via the `configuration.yaml` file, where `bm_feed` object have to be created.

```yaml
bm_feed:
  triggers:
    - ">MYCALL" # Capture all calls to MYCALL
    - ">#12345" # Capture all calls to ID 12345
    - ">@#1234" # Capture all calls to TG 1234
    - "<YMCALL" # Capture all calls from YMCALL
    - "<#12345" # Capture all calls from ID 12345
```

Simple LALR grammar is provided, which allows to combine filters by using "and" `&`, "or" `|` and "not" `!` operators together with "parentheses" `()`.
The last is required as all operators have same precedence.

```yaml
">MYCALL&!(<YMCALL|<#12345)" # Capture all calls to MYCALL and not from YMCALL or ID 12345 
```


## TODO

- Replace dictionary mayhem with more sophisticated type and logic system.
- Add sensors or different entities representing filter results.
- Create config flow.
