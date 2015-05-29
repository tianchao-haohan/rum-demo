define(['lodash'],
function (_) {
  "use strict";

  return function Settings (options) {
    /**
     * To add a setting, you MUST define a default. Also,
     * THESE ARE ONLY DEFAULTS.
     * They are overridden by config.js in the root directory
     * @type {Object}
     */
    var defaults = {
      /*elasticsearch     : "https://"+window.location.hostname+":9200",*/
      elasticsearch     : "https://"+window.location.hostname,
      api_version       : "1.0",
      sniff             : false,
      request_timeout   : 30000,
      panel_names       : [],
      kibana_index      : 'kibana-int',
      default_route     : '/dashboard/file/IntFlow+ALL.json'
    };

    // This initializes a new hash on purpose, to avoid adding parameters to
    // config.js without providing sane defaults
    var settings = {};
    _.each(defaults, function(value, key) {
      settings[key] = typeof options[key] !== 'undefined' ? options[key]  : defaults[key];
    });

    return settings;
  };
});
