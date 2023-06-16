/* Download Data */

symkey = sessionStorage.getItem("symkey");
privateKey = atob(sessionStorage.getItem("privatekey"));
publicKey = atob(sessionStorage.getItem("publicKey"));

let role = document.getElementById("role").value

window.onload = async function () {

    try {
        var data = document.getElementById('files').value;
    } catch (error) {
        var data = false;
    };
    
    if(data){
        data = data.replaceAll("'", '"');
        data = data.replaceAll("None", 'null');

        var filename = "Folder.json";
        var data_json = JSON.parse(data)
        
        for(i in data_json){
            data_json[i]["name"] = await decrypt_file(data_json[i]["name"]);
            data_json[i]["content"] = await decrypt_file(data_json[i]["content"]);
        };

        data = JSON.stringify(data_json)
        document.getElementById("files").value = data
        download(data, filename);
    };

    try {
        var pendingFiles = document.getElementById('pendingFile').value;
    } catch (error) {
        var pendingFiles = false;
    };

    if(pendingFiles){
        pendingFiles = pendingFiles.replaceAll("'", '"');
        pendingFiles = pendingFiles.replaceAll("None", 'null');

        var filename = "pendingFiles.json";
        var pendingFiles_json = JSON.parse(pendingFiles)
        
        for(i in pendingFiles_json){
            pendingFiles_json[i]["name"] = await decrypt_file(pendingFiles_json[i]["name"]);
            pendingFiles_json[i]["content"] = await decrypt_file(pendingFiles_json[i]["content"]);
        };

        pendingFiles = JSON.stringify(pendingFiles_json)
        document.getElementById("pendingFile").value = pendingFiles
        download(pendingFiles, filename);
    };
    
    try {
        var accords = document.getElementById('accords').value;
    } catch (error) {
        var accords = false;
    };

    if(accords){
        accords = accords.replaceAll("'", '"');
        accords = accords.replaceAll("None", 'null');
        if(role == "DOCTOR"){
            data_json = JSON.parse(accords)
            for(i in data_json){
                data_json[i]["protected_symetric_key"]=decrypt(data_json[i]["protected_symetric_key"])
            }
            accords =  JSON.stringify(data_json)
        };
        document.getElementById('accords').value = accords;
        download(accords, "Accords.json");
    };
}

function download(data, filename) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(data));
    element.setAttribute('download', filename);
    element.style.display = "none";
    element.click();
}

async function decrypt_file(elem){
    
    elem = atob(elem).split("|");
    
    var encrypted = forge.util.createBuffer(forge.util.hexToBytes(elem[0]));
    var iv = atob(elem[1]);
    var tag = forge.util.createBuffer(forge.util.hexToBytes(elem[2]));

    decryptTitle = await decryptMessage(
        forge.util.createBuffer(forge.util.hexToBytes(symkey), "raw"),
        encrypted,
        iv,
        tag
    );

    return decryptTitle.output.data;
}

function decrypt(encrypSymkey){
    let privKey = forge.pki.privateKeyFromPem(privateKey);;
    decryptSymKey = privKey.decrypt(atob(encrypSymkey));
    return decryptSymKey
}