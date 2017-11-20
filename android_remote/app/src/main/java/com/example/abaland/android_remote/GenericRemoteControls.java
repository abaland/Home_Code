package com.example.abaland.android_remote;

class GenericRemoteControls {

    /**
     * Converts the KeyToPressName into a XML-formatted instruction which presses that button
     *
     * @param remoteName Name of the remote according to rabbitmq
     * @param ConfigToSend Key that must be pressed
     */
    String convertToXmlInstruction(String remoteName, String ConfigToSend){

        String messageToSend;

        messageToSend = "<instruction" +
                " type=\"remote_control\"" +
                " target=\"bedroom,living\"" +
                " remote=\"" + remoteName + "\"" +
                " config=\"" + ConfigToSend + "\"" +
                "/>";

        ////////////////////////
        return messageToSend;
        ////////////////////////

    }

}
