window.onload = async function () {
  titleArray = [];
  var symkey = sessionStorage.getItem("symkey");
  try {
    var accord = document.getElementById("accord")

  } catch (error) {
    var accord = false

  }

  if (accord) {
    privateKey = atob(sessionStorage.getItem("privatekey"));
    let privKey = forge.pki.privateKeyFromPem(privateKey);
    symkey = privKey.decrypt(atob(accord.value));

  }

  for (element in document.getElementsByClassName("filename-title")) {
    if (
      document.getElementsByClassName("filename-title")[element].textContent !==
      undefined
    ) {
      titleArray.push(
        atob(document.getElementsByClassName("filename-title")[element].textContent)
      );
    }
  }

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

    document.getElementsByClassName("filename-title")[index].textContent =
      decryptTitle.output.data;
  }
};
