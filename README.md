# Pentaho Suite Validation

The current script will download each Pentaho tool, not plugin, and guarantee we are able to run each tool CE and EE successful without any error.

In Jenkins this project must be the first to execute, because are going to download and start the tools, it means we are working on a fresh installation, on the first start of the tool.