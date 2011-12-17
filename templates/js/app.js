function logItem(logObj) {
    if (!logObj.name || !logObj.src)
        return {};
    
    /* default options */
    var defaults = {
        isActive: true,
        messages: [],
        screens: [],
        error: ''
    }
    
    defaults = $.extend(defaults, logObj);

    return {
        name : ko.observable(defaults.name),
        src : ko.observable(defaults.src),
        isActive : ko.observable(defaults.isActive),
        messages : ko.observableArray(defaults.messages),
        screens : ko.observableArray(defaults.screens),
        error: ko.observable(defaults.error),
        remove : function() {
            if (!confirm('Are you sure you want to delete "' + this.src() + '"?')) {
                return;
            }
            app.removeLog(this.src());
        },
        edit : function() {
            app.editLog(this.src());
        },
        isActiveScreenLog: function() {
            var activeScreenName = app.data.activeScreen()[0].name();
                
            if (!activeScreenName || -1 == this.screens().indexOf(activeScreenName)) {
                return false;
            }
            
            return true;
        },
        setErrorClass: function() {
            return this.error() == '' ? '' : 'error';
        }
    }
}

function logScreen(screenObj) {
    if (!screenObj.name)
        return {};

    return {
        name : ko.observable(screenObj.name),
        isActive : ko.observable(screenObj.isActive || false),
        remove : function() {
            if (!confirm('Are you sure you want to delete screen "' + this.name() + '"?')) {
                return;
            }
            app.removeScreen(this.name());
        },
        setActive : function() {
            app.setActiveScreen(this.name());
        },
        isNotDefault: function() {
            return this.name() == app.DEFAULT_SCREEN_NAME ? false : true;
        }
    }
}

/* this object gives simple interface for command listening/pushing (io.Socket) */
var dataListener = {
    
    _addConstants : function() {
        this.MESSAGE_ENTRY = 'entry';
        this.MESSAGE_STATUS = 'status';
        this.STATUS_ERROR = 'error';
    },    
    
    init : function() {
        var hoc = this;
        
        this._addConstants();

        this.connect();
        this.bindEvents();
    },

    connect : function() {
        this.listener = new SockJS(settings.io.host);
    },

    bindEvents : function() {
        var hoc = this;

        this.listener.onopen = function(e) {
            hoc.follow(app.getLogList());
        };

        this.listener.onmessage = function(m) {
            // TODO: Error handling?
            if (m.type == 'message') {
                app.update(JSON.parse(m.data));
            }
        };

        // TODO: Implement front-end logic for server disconnect
        // this.listener.onclose = function() {
        //   this.listener = null;
        // };
    },

    follow : function(logs) {
        logs = logs || [];

        if (!logs.length) {
            return;
        }
        this._push('follow', logs);
    },

    unfollow : function(logs) {
        logs = logs || [];

        if (!logs.length) {
            return;
        }
        this._push('unfollow', logs);
    },

    _push : function(command, logs) {
        this.listener.send(JSON.stringify({
            'command' : command,
            'logs' : logs
        }));
    }
}

var dataStorage = {
    init : function() {
    },

    loadData : function() {
        if (!localStorage.getItem('logfollow')) {
            return this._loadFixtures();
        }
        
        return JSON.parse(localStorage.getItem('logfollow'));
    },

    saveData : function(data) {
        var dataToSave = this._sanitizeData(data);
        return localStorage.setItem('logfollow', dataToSave);
    },
    
    clearData : function() {
        return localStorage.removeItem('logfollow');
    },

    _loadFixtures : function() {
        return {
            logs : [ 
            {
                'name' : 'Apache log', 
                'src' : '/var/log/apache2/access.log', 
                'isActive' : true,
                'screens' : ['_default']
            }
            ],
            screens : [ 
            {
                'name' : '_default', 
                'isActive': true 
            }
            ]
        };
    },

    /* clear data before save (do not save messages and status for logs) */
    _sanitizeData : function(data) {
        var sanitizedObj = ko.mapping.toJS(data) || {};
		
        for ( var logIndex in sanitizedObj.logs) {
            sanitizedObj.logs[logIndex]['messages'] = [];
            sanitizedObj.logs[logIndex]['error'] = '';
        //sanitizedObj.logs[logIndex]['isActive'] = true;
        }

        return JSON.stringify(sanitizedObj);
    }
}

/**
 * main app controller
 */
app = {
    init: function() {
        /* init constants */
        this.initConstants();
        
        /* init data storage */
        this.storage = dataStorage;
        this.storage.init();
        
        /* load saved data from storage */
        this.data = this.storage.loadData();
        
        /* init knockout model */
        this.initViewModel();

        /* init signal listener */
        this.listener = dataListener;
        this.listener.init();
        
        /* init inner bindings */ 
        /* only save for now */
        this._bindEvents();
    },
      
    initConstants : function() {
        this.DEFAULT_SCREEN_NAME = '_default';
    },

    initViewModel : function() {
        var hoc = this;
        
        var mapping = {
            'logs': {
                create: function(options) {
                    return new logItem(options.data);
                }
            },
            'screens': {
                create: function(options) {
                    return new logScreen(options.data);
                }
            }
        }
        
        this.data = ko.mapping.fromJS(this.data, mapping);
        
        this.data.staticText = {
            greeting : "Hello, you are new here. Add your first log below",
            addLogMessage : "Add new log",
            addScreenMessage : "Add new screen"
        };
        
        this.data.activeScreen = ko.dependentObservable(function() {
            return ko.utils.arrayFilter(hoc.data.screens(), function(screen) {
                return screen.isActive() == true;
            });
        }, this.data);
        
        this.data.isFirstLog = ko.dependentObservable(function() {
            return hoc.data.logs().length > 0 ? false : true;
        }, this.data);
		
        ko.applyBindings(this.data);
    },

    /* return array of log sources to listen on socket connect */
    getLogList : function() {
        var logList = [];
        var data = ko.toJS(this.data.logs);
        for ( var logIndex in data) {
            if (data[logIndex]['src']) {
                logList.push(data[logIndex]['src']);
            }
        }

        return logList;
    },

    /* this method apply on socket message receive */
    update : function(data) {
        if (!data || !data.type) {
            return;
        }
          
        if (data.type == dataListener.MESSAGE_ENTRY) {
            this.addLogMessage(data);
        }
        
        if (data.type == dataListener.MESSAGE_ENTRY && data.status == dataListener.STATUS_ERROR) {
            this.addLogError(data);
        }
        
    },

    addScreen : function(form) {
        var screenName =  $("#screen-name", form).val();
        if ('' == screenName || app.checkScreenExist(screenName)) {
            return;
        }

        var screen = new logScreen({
            'name' : screenName
        });

        app.data.screens.push(screen);
        
        /* clear the form after item add */
        $("input[type=text], select", form).val('');
    },

    removeScreen : function(name) {
        var screens = ko.toJS(this.data.screens);
        for (var i in screens) {
            if (screens[i].name == name) {
                this.data.screens.splice(i, 1);
            }
        }
		
        /* XXX maybe not need due to ko */
        var logs = ko.toJS(this.data.logs);
        for (var i in logs) {
            var removeIndex = logs[i].screens.indexOf(name);
            if (-1 != removeIndex) {
                this.data.logs()[i].screens.splice(removeIndex, 1);
            }

            /* last screen removed - move to _default */
            if (!this.data.logs()[i].screens().length) {
                this.data.logs()[i].screens.push(app.DEFAULT_SCREEN_NAME);
            }
        }

    },
	
    checkScreenExist: function(name) {
        var screens = ko.toJS(this.data.screens);
        for (var i in screens) {
            if (screens[i].name == name) {
                return true;
            }
        }
        return false;
    },   
    
    setActiveScreen : function(name) {
        var screens = ko.toJS(this.data.screens), 
        newActiveIndex = -1,
        oldActiveIndex = -1;
		
        for (var i in screens) {
            if (screens[i].name == name) {
                newActiveIndex = i;
            }
			
            if (screens[i].isActive) {
                oldActiveIndex = i;
            }
        }
		
        /* XXX ko should make it automatically */
        if (-1 != newActiveIndex && newActiveIndex != oldActiveIndex ) {
            this.data.screens()[newActiveIndex].isActive(true);
            
            if (-1 != oldActiveIndex) {
                this.data.screens()[oldActiveIndex].isActive(false);
            } 
        }
    },
    
    checkLogExist: function(source) {
        var logs = ko.toJS(this.data.logs);
        for (var i in logs) {
            if (logs[i].src == source) {
                return true;
            }
        }
        return false;
    },

    addLog : function(form) {
        var screenNames = $("select", form).val(),
        logName =  $("#log-name", form).val(),
        logSource =  $("#log-source", form).val();
            
        if ('' == logSource || app.checkLogExist(logSource)) {
            return;
        }

        var log = new logItem({
            'name' : logName || logSource,
            'src' : logSource
        });
        
        for (var key in screenNames) {
            if (app.checkScreenExist( screenNames[key] )) {
                log.screens.push( screenNames[key] );
            }
        }

        if (!log.screens().length) {
            return;
        }

        $("input[type=text]", form).val('');
        
        
        
        app.data.logs.push(log);
        app.listener.follow([logSource]);
        
        $('#log-holder').isotope('reloadItems').isotope({sortBy: "original-order"});
              
    },

    addLogMessage : function(data) {
        if (!data.log || !this.checkLogExist(data.log) || !data.entries.length) {
            return;
        }
        
        /* XXX maybe not need due to ko */
        var logs = ko.toJS(app.data.logs);
        for (var i in logs) {
            if (data.log == logs[i].src) {  
                for (var m in data.entries) {
                    app.data.logs()[i].messages.push(data.entries[m]);
                }
                /* remove error string if new entry come */
                app.data.logs()[i].error('');
                break;
                
            }
        }
    },
    
    addLogError : function(data) {
        if (!data.log || !this.checkLogExist(data.log)) {
            return;
        }
        
        /* XXX maybe not need due to ko */
        var logs = ko.toJS(app.data.logs);
        for (var i in logs) {
            if (data.log == logs[i].src) {  
                app.data.logs()[i].error(data.description);
                break;
                
            }
        }
    },

    removeLog : function(src) {
        var logs = ko.toJS(this.data.logs);
        for (var i in logs) {
            if (logs[i].src == src) {
                this.data.logs.splice(i, 1);
            }
        }
        
        app.listener.unfollow([src]);
        $('#log-holder').isotope('reLayout');
    },
        
    clearAll: function() {
        if (!confirm('Are you sure you want to delete all data?')) {
            return;
        }
        
        app.storage.clearData();
        app.data = {};
        
        window.location.href = '/';
    },

    _bindEvents : function() {
        var hoc = this;

        /* simple but lame */
        setInterval(function() {
            hoc.storage.saveData(hoc.data)
        }, 5000);
        
        /* toDo create pop-up manager */
        /* XXX remove this later */
        $('#showAddForm').click(function(e) {
            e.preventDefault();
            $('.overlay').hide();
            $('#log-form-holder').show();
        });
        
        $('#showAddScreen').click(function(e) {
            e.preventDefault();
            $('.overlay').hide();
            $('#screen-form-holder').show();
        });
        
        $('.holder .close').click(function(e) {
            e.preventDefault();
            $('.overlay').hide();
        });
        
        /* add isotope */            
        $('#log-holder').isotope({
            itemSelector : '.item',
            layoutMode : 'fitRows'
        });
    }
}
