function logItem(logObj) {
	if (!logObj.name || !logObj.src)
		return {};

	return {
		guid : logObj.guid || app.generateLogGuid(),
		name : ko.observable(logObj.name),
		src : ko.observable(logObj.src),
		isActive : ko.observable(logObj.isActive || true),
		messages : ko.observableArray(logObj.messages || []),
		categories : ko.observableArray()
	}
}

function logCategory(catObj) {
	if (!catObj.name)
		return {};

	return {
		name : ko.observable(catObj.name),
		isActive : ko.observable(catObj.isActive || true),
		remove : function() {
			app.removeCategory(this.name());
		},
		setActive : function() {
			app.setActiveCategory(this.name());
		}
	}
}

/* this object gives simple interface for command listening/pushing (io.Socket) */
var dataListener = {
	init : function() {
		var hoc = this;

		this.listener = new io.Socket(settings.io.host, {
			port : settings.io.port,
			rememberTransport : false
		});

		/* XXX app method call */
		this.listener.addEvent('connect', function(e) {
			hoc.follow(app.getLogList());
		});

		this.bindEvents();
		this.connect();
	},

	connect : function() {
		this.listener.connect();
	},

	bindEvents : function() {
		var hoc = this;

		/* XXX app method call */
		this.listener.addEvent('message', function(data) {
			app.update(data);
		});
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
		this.listener.send({
			'command' : command,
			'logs' : logs
		});
	}
}

var dataStorage = {
	init : function() {
	},

	loadData : function() {
		return localStorage.getItem('logfollow') || this._loadFixtures();
	},

	saveData : function(data) {
		var dataToSave = this._sanitizeData(data);
		return localStorage.setItem('logfollow', dataToSave);
	},

	_loadFixtures : function() {
		return {
			greeting : {
				text : "Hello, you are new here. Add your first log below"
			},
			logs : ko.observableArray(),
			categories : ko.observableArray([ new logCategory({name : 'default'}) ])
		};
	},

	/* clear data before save (do not save messages and status for logs) */
	_sanitizeData : function(data) {
		var sanitizedObj = data || {};

		for ( var logIndex in sanitizedObj.logs) {
				delete sanitizedObj.logs[logIndex]['messages'];
				delete sanitizedObj.logs[logIndex]['isActive'];
		}

		return ko.mapping.toJS(sanitizedObj);
	}
}

app = {
	init: function() {

	   this.storage = dataStorage;
       this.storage.init();

		/* for test only */
		localStorage.removeItem('logfollow');
		this.data = this.storage.loadData(); 
		this.initViewModel();

		this.maxLogGuid = this.findMaxGuid();

		this.listener = dataListener.init();
		this._bindEvents();
	},

	initViewModel : function() {
		this.data = ko.mapping.fromJS(this.data);
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

	findMaxGuid : function() {
		var guid = 1;
		var data = ko.toJS(this.data.logs);
		for ( var logIndex in data) {
			if (data[logIndex]['guid']
					&& parseInt(data[logIndex]['guid'], 10) > guid) {
				guid = parseInt(data[logIndex]['guid'], 10);
			}
		}

		return guid;
	},

	generateLogGuid : function() {
		return ++this.maxLogGuid;
	},

	/* this method apply on socket message receive */
	update : function(message) {

	},

	addCategory : function(catObj) {

	},

	removeCategory : function(name) {
		var categories = ko.toJS(this.data.categories);
		for (var i in categories) {
			if (categories[i].name == name) {
				this.data.categories.splice(i, 1);
			}
		}
		
		/* XXX maybe not need due to ko */
		var logs = ko.toJS(this.data.logs);
		for (var i in logs) {
			if (-1 != logs[i].categories.indexOf(name)) {
				var removeIndex = logs[i].categories.indexOf(name);
				this.data.logs[i].categories.splice(removeIndex, 1);
			}
		}

	},
	
	checkCategoryExist: function(name) {
		var categories = ko.toJS(this.data.categories);
		for (var i in categories) {
			if (categories[i].name == name) {
				return true;
			}
		}
		return false;
	},

	setActiveCategory : function(name) {
		var categories = ko.toJS(this.data.categories);
		var newActiveIndex = -1;
		var oldActiveIndex = -1;
		
		for (var i in categories) {
			if (categories[i].name == name) {
				newActiveIndex = i;
			}
			
			if (categories[i].isActive) {
				oldActiveIndex = i;
			}
		}
		
		/* XXX ko should make it automatically */
		if (-1 != newActiveIndex && newActiveIndex != oldActiveIndex ) {
			this.data.categories[oldActiveIndex].isActive = false;
			this.data.categories[newActiveIndex].isActive = true;
		}
	},

	addLog : function(form) {
		var categoryName = $("select", form).val();
        var logName =  $("#log-name", form).val();
		var logSource =  $("#log-source", form).val();
		if ('' == logSource || '' == logName || !app.checkCategoryExist(categoryName)) {
			return;
		}

		var log = new logItem({
				'name' : logName,
				'src' : logSource
				});
		log.categories.push(categoryName);
		app.data.logs.push(log);
	},

	addLogMessage : function(guid, message) {

	},

	/* single integer(string) guid value allowed */
	removeLogs : function(guids) {

	},

	_bindEvents : function() {
		var hoc = this;

		/* simple but lame */
		setInterval(hoc.storage.saveData(hoc.data), 2500);
	}
}
