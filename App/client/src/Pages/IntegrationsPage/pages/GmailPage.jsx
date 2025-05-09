import AnimatedGridPattern from "@/Components/magicui/animated-grid-pattern";
import { LinkPreview } from "@/Components/ui/link-preview";
import GmailLogo from "@/assets/gmail.svg";
import { cn } from "@/lib/utils";

export default function GmailPage() {
  return (
    <div className="max-h-screen overflow-y-auto">
      <AnimatedGridPattern
        numSquares={40}
        maxOpacity={0.5}
        duration={3}
        repeatDelay={1}
        className={cn(
          "[mask-image:radial-gradient(600px_circle_at_center,white,transparent)]",
          "inset-x-[20%] h-screen skew-y-12"
        )}
      />
      <div className="flex flex-col justify-start gap-y-5 w-[98%]">
        <h2 className="text-3xl font-semibold text-primary border-b pb-2">
          Gmail Integration Setup Guide
        </h2>
        <div className="flex h-fit">
          <div className="w-[50%]">
            <h3 className="scroll-m-20 text-2xl font-semibold tracking-tight">
              Overview
            </h3>
            <div className="text-justify">
              Gmail is a free email service provider. NeuraCRM allows users to
              seamlessly interact with their gmail through a chatbot interface.
              By integrating Gmail with our service, users can perform various
              actions such as sending Gmails. This page documents the the
              resources available for Gmail on our platform, as well as a
              guideline for setting up the Gmail resources on our 'Actions'
              page.
              <br />
              <br />
              Before integrating Gmail with NeuraCRM, you need a valid Google
              account as well as a valid Google application password. &nbsp;
              <LinkPreview
                className="text-blue-600 font-semibold hover:opacity-80 transition-opacity"
                url="https://support.google.com/accounts/answer/185833?hl=en"
              >
                See here for more details.
              </LinkPreview>
            </div>
          </div>
          <div className="w-[50%] h-full flex justify-center items-center">
            <img
              src={GmailLogo}
              alt="Gmail Logo"
              className="w-[30%] h-[30%] ml-10"
            />
          </div>
        </div>

        <h3 className="scroll-m-20 text-2xl font-semibold tracking-tight">
          Selecting the desired Gmail Service:
        </h3>
        <p>
          When you want to create a new Gmail action, select 'API' as your
          desired action type, then from the 'API Service' dropdown menu, select
          'Gmail' as your API service.
          <br />
          <br />
          <sup>
            As of v1.0 of NeuraCRM, only the sending of Gmail is supported.
          </sup>
        </p>
        <h3 className="scroll-m-20 text-2xl font-semibold tracking-tight">
          Sending Gmail:
        </h3>
        <div>
          To create an action for enabling the sending of Gmail using our
          service, follow these detailed steps to fill in the required fields:
          <ol className="list-decimal list-inside mt-5">
            <li className="mb-2">
              <span className="font-semibold">Action Name:</span> Provide a
              descriptive name for the action. The name should be in lowercase
              and use underscores (_) instead of whitespace.
              <br />
              <p className="ml-4 mt-2">
                Example: <code>send_gmail</code>
              </p>
            </li>
            <li className="mb-2">
              <span className="font-semibold">Description:</span> Enter a
              detailed description that clearly explains what the action does.
              This helps in understanding the purpose of the action at a glance.
              <br />
              <p className="ml-4 mt-2">
                Example: <code>Send Gmail with the given details.</code>
              </p>
            </li>
            <li className="mb-2">
              <span className="font-semibold">API Domain:</span> Input{" "}
              <code>smtp.gmail.com</code> into this field.
              <br />
            </li>
            <li className="mb-2">
              <span className="font-semibold">Auth Parameter Fields:</span> You
              will need to fill in one specific authentication parameters to
              authorize your Gmail actions. This parameters ensure that the
              requests are authenticated and secure.
              <br />
              <ul className="list-disc list-inside mt-2 ml-4">
                <li className="mb-2">
                  <span className="font-semibold">Key:</span> Your Gmail
                  address.
                  <p className="ml-4 mt-2">
                    Example: <code>user@gmail.com</code>
                  </p>
                </li>
                <li className="mb-2">
                  <span className="font-semibold">Value:</span> Your Google
                  application password. Obtain this password following the link
                  to the guide above
                  <p className="ml-4 mt-2">
                    Example: <code>abcd efgh ijkl mnop</code>
                  </p>
                </li>
              </ul>
              <p className="ml-4 font-medium text-xs">
                Note: It is crucial to have exactly one field when submitting
                the form, with the key being the correct email address and the
                value being a valid google application password.
              </p>
            </li>
            <li className="mb-2">
              <span className="font-semibold">Input section:</span> You need to
              provide the following inputs to send a Gmail. The inputs should be
              exactly <code>email_subject</code>, <code>email_body</code> and{" "}
              <code>email_recipient</code>.
            </li>
            <li className="mb-2">
              <span className="font-semibold">Output section:</span> Leave the
              output section empty as it is not required.
            </li>
          </ol>
        </div>
        <h3 className="scroll-m-20 text-2xl font-semibold tracking-tight">
          Read Gmail:
        </h3>
        <p className="mb-[50vh]">
          This service is not supported in the current version of NeuraCRM.
          We are working on adding this feature in the future.
        </p>
      </div>
    </div>
  );
}
