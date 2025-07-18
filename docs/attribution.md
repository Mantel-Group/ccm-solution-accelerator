# Attribution

Attribution is the process of assigning ownership to a resource, to allow the dashboard to slice and dice data based on different business units, geographical location, or any other attribute that you may like to use.

The tool has support for attribution, however the asset register required to achieve this is not provided, as it is custom for each engagement.  In order to achieve attribution, you can provide a csv file, or, build some automation to produce this file before hand.

The attribution file is stored as [seed__asset_register.csv](../datapipeline/seeds/seed__asset_register.csv) and has the following format.

| resource_type | resource | business_unit | team    | location | owner  | active |
|---------------|----------|---------------|---------|----------|--------|--------|
| `JQ12345`     | `laptop` | `Marketing`   | `Sales` | `Sydney` | `Phil` | `true` |
