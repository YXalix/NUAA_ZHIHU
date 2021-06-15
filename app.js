var pg = require('pg');
const pgClient = require('pg').Client;

//var conString = ":zhp@521224//myself:zhp@521224@124.70.46.225:26000/postgres";
var cn = {
    host: '124.70.46.225', // server name or IP address;
    port: 26000,
    database: 'postgres',
    user: 'myself',
    password: 'zhp@521224'
};
//var client = new pgClient(conString);
var client = new pgClient(cn);

client.connect(err => {
    if (err) throw err;
    else {
        createDatabase();
        client.end(console.log('close client connection'));
    }
});



function createDatabase(){
    const command = `
    DROP TABLE IF EXISTS inventory;
    CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);
    `;
    client
        .query(command)
        .then(() => {
            console.log('Table created successfully!');
            client.end(console.log('Closed client connection'));
        })
        .catch(err => console.log(err))
        .then(() => {
            console.log('Finished execution, exiting now');
            process.exit();
        });
}