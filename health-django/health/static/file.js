async function decryptFile() {
  titleArray = [];

  symkey = sessionStorage.getItem("symkey");
  let accord = null

  try {
    accord = document.getElementById("accord")
  } catch (error) {
    accord = false
  }

  if (accord) {
    privateKey = atob(sessionStorage.getItem("privatekey"));
    let privKey = forge.pki.privateKeyFromPem(privateKey);
    decryptSymKey = privKey.decrypt(atob(accord.value));
    symkey = decryptSymKey;
  }


  titleArray.push(atob(document.getElementById("id_name").value));
  titleArray.push(atob(document.getElementById("id_content").textContent));

  for (index in titleArray) {
    title = titleArray[index].split("|");

    var encrypted = forge.util.createBuffer(forge.util.hexToBytes(title[0]));
    var iv = atob(title[1]);
    var tag = forge.util.createBuffer(forge.util.hexToBytes(title[2]));

    decryptTitle = await decryptMessage(
      forge.util.createBuffer(forge.util.hexToBytes(symkey), "raw"),
      encrypted,
      iv,
      tag
    );

    if (index == 0) {
      document.getElementById("id_name").value = decryptTitle.output.data;
    } else {
      document.getElementById("id_content").textContent = decryptTitle.output.data;
    }
  }
};
