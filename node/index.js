var express = require('express');

var hbs = require('express-handlebars').create({
  defaultLayout: 'main',
  extname: '.hbs',
  layoutsDir: __dirname + '/views/layouts'});
var app = express();

app.set('port',process.env.PORT || 8080);
app.engine('hbs',hbs.engine);
app.set('view engine','hbs');
//app.set('views', '/home/workspace/rum-demo/node/views');
app.set('views', __dirname +  '/views');


app.use(express.static(__dirname + '/public'));

app.get('/', function (req, res) {
  res.render('home',{
    title:'Home Page'
  });
});

app.get('/about', function (req, res) {
  res.render('about',{
    title:'About Page'
  });
});

app.get('/serviceGroup', function (req, res) {
  res.render('serviceGroup',{
    title:'服务组性能健康状况'
  });
});

app.get('/serviceGroupDetails', function (req, res) {
  res.render('serviceGroupDetails',{
    title:'服务组各服务性能健康状况'
  });
});

app.get('/serviceDetailsByServer', function (req, res) {
  res.render('serviceDetailsByServer',{
    title:'服务在各服务器上性能状况'
  });
});

app.get('/serviceDetailsInSpecificServer', function (req, res) {
  res.render('serviceDetailsInSpecificServer',{
    title:'服务在单一服务器上性能状况'
  });
});

app.get('/serverMonitoring', function (req, res) {
  res.render('serverMonitoring',{
    title:'服务器监控'
  });
});

app.get('/serverNetworkPerformance', function (req, res) {
  res.render('serverNetworkPerformance',{
    title:'服务器网络性能'
  });
});

app.get('/subNetNetworkPerformance', function (req, res) {
  res.render('subNetNetworkPerformance',{
    title:'子网网络性能'
  });
});

app.listen(app.get('port'), function () {
  console.log( 'Server Started, port: '+app.get('port') );
});


