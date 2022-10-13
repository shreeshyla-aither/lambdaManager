var aws = require("aws-sdk");
var ses = new aws.SES({ region: "us-east-1" });
exports.handler = async function (event) {
  var params = {
    Destination: {
      ToAddresses: ["shreeshyla@aithertechnology.com"],
    },
    Message: {
      Body: {
        Text: { Data: "Test" },
      },

      Subject: { Data: "Test Email" },
    },
    ReplyToAddresses: ["123456@cforia.aithertechnology.com"],
    ReturnPath: "return_123456@cforia.aithertechnology.com",
    Source: "noreply@aithertechnology.com",
  };
 
  return ses.sendEmail(params).promise()
};