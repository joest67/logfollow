function logItem(logObj) {
   if (!logObj.name || !logObj.src || !logObj.catGuid) return {};

   return {
       catGuid: logObj.catGuid,
       name: ko.observable(logObj.name),
       src: ko.observable(logObj.src),
       isActive: ko.observable(logObj.isActive || true),
       messages: ko.observableArray(logObj.messages || [])
   }
}

function logCategory(catObj) {
    if (!catObj.name) return {};

    return {
       guid: catObj.guid || app.generateCatLogGuid(),
       name: ko.observable(catObj.name),
       isActive: ko.observable(catObj.isActive || true),
       logs: ko.observableArray(catObj.messages || []),
       remove: function() {
	   app.removeCategory(this.guid());
       },
       setActive: function() {
	   app.setActiveCategory(this.guid());
       }
    }	
}

/* this object gives simple interface for command listening/pushing (io.Socket) */
var dataListener = {
	init: function() {

	   this.listener = new io.Socket(window.location.hostname, {
		 port: 8001,
		 rememberTransport: false
	   });

       /* XXX app method call */
	   this.listener.addEvent('connect', function(e) {
 	       hoc.follow(app.getLogList());
	   });

	   this.bindEvents();
	   this.connect();
	},

    connect: function() {
	   this.listener.connect();
	},

    bindEvents: function() {
	   var hoc = this;

	   /* XXX app method call */
	   this.listener.addEvent('message', function(data) {
	      app.update(data);
	   });
	},

    follow: function(logs) {
       logs = logs || [];
        
       if (!logs.length) {
          return;
       }
	   this._push('follow', logs);
	},

	unfollow: function(logs) {
       logs = logs || [];
        
       if (!logs.length) {
          return;
       }
	   this._push('unfollow', logs);
	},

	_push: function(command, logs) {
	   this.listener.send({'command': command, 'logs': logs});
	}
}

var dataStorage= {
	init: function() {
	},

    loadData: function() {
       return localStorage.getItem('logfollow') || this._loadFixtures();
	},

	saveData: function(data) {
	    var dataToSave = this._sanitizeData(data);
	    return localStorage.setItem('logfollow', dataToSave);
	},

	_loadFixtures: function() {
	   return { greeting: {
		  		text: "Hello, you are new here. Add your first log below",
		  		newLog: ko.observable("Log name")
	      		},
			categories: ko.observableArray([new logCategory({name: 'default'})])
       };
	},

        /* clear data before save (do not save messages and status for logs) */
    _sanitizeData: function(data) {
	    var sanitizedObj = data || {};

	    for (var catIndex in sanitizedObj.categories) {
		for (var logIndex in sanitizedObj.categories[catIndex]) { 
                     delete sanitizedObj.categories[catIndex][logIndex]['messages'];
                     delete sanitizedObj.categories[catIndex][logIndex]['isActive'];
                }
            }

        return sanitizedObj;
	}
}

app = {
	init: function() {

	   this.storage = dataStorage;
       this.storage.init();

	   this.data = this.storage.loadData();

       this.maxCatGuid = this.findMaxCatGuid();

	   this.initViewModel();

	   this.listener = dataListener.init();
	   this._bindEvents();
	},

	initViewModel: function() {
	   ko.applyBindings(this.data);
	},

        /* return array of log sources to listen on socket connect */
    getLogList: function() {
	   var logList = [];
           var data = this.data.categories;
           for (var catIndex in data) {
		for (var logIndex in data[catIndex]) { 
                     if (data[catIndex][logIndex]['src']) {
                         logList.push(data[catIndex][logIndex]['src']);
		     }  
                }
	   }

           return logList;
        },

    findMaxCatGuid: function() {
	   var guid = 1;

           var data = this.data.categories;
           for (var catIndex in data) {
             if (data[catIndex]['guid'] && parseInt(data[catIndex]['guid'], 10) > guid) {
                 guid = parseInt(data[catIndex]['guid'], 10);
	     }  
	   }

           return guid;
        },

    generateCatLogGuid: function() {
             return ++this.maxCatGuid;
        },

	/* this method apply on socket message recieve */
    update: function(message) {
	
        },

	addCategory: function(catObj) {
		
        },

    removeCategory: function(guid) {

        },

    setActiveCategory: function(guid) {

        },

	addLog: function(logObj) {

        },

    addLogMessage: function(guid, message) {

        },

	/* single integer(string) guid value allowed */
	removeLogs: function(guids) {

        },

	_bindEvents: function() {
	   var hoc = this;

       /* simple but lame */
       setInterval(hoc.storage.saveData(hoc.data), 2500);
	}
}

