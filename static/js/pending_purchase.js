const verifyPurchase = async (client_id) => {
  const endpointUrl = `/api/verify_purchase/${client_id}`;
  const response = await (await fetch(endpointUrl)).json();

  console.log(response);
  location.reload();
};
