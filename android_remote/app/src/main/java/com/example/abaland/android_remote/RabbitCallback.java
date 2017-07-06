package com.example.abaland.android_remote;

/**
 * Generic interface to process one message received from RabbitMQ server, after the sanity checks
 * have been made
 */
interface RabbitCallback {

    /**
     * Executes callback function on the message
     *
     * @param messageToProcess XML string with all information to process
     */
    void execute(String messageToProcess);

}
