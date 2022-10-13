var aws = require("aws-sdk");
var ses = new aws.SES({ region: "us-east-1" });
exports.handler = async function (event) {
  var params = {
    Destination: {
      ToAddresses: ["nick@aithertechnology.com"],
    },
    Message: {
      Body: {
        Text: { Data: "Test" },
      },

      Subject: { Data: "Test Email" },
    },
    ReplyToAddresses: ["12345@cforia.aithertechnology.com"],
    ReturnPath: "return_12345@cforia.aithertechnology.com",
    Source: "noreply@aithertechnology.com",
  };
 
  return ses.sendEmail(params).promise()
};