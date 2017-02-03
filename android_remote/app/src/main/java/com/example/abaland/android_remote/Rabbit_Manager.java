package com.example.abaland.android_remote;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.io.IOException;
import java.util.concurrent.TimeoutException;


class Rabbit_Manager {

    private ConnectionFactory factory = new ConnectionFactory();
    private Connection connection;
    private Channel channel;

    private String InstructionName = "remote_control";


    Rabbit_Manager() {

        String HostIp = "192.168.3.7";
        String RabbitUser = "adrien";
        String RabbitPassword = "password";

        // Initializes connectionFactory parameters, to start connexions with server
        factory.setHost(HostIp);
        factory.setUsername(RabbitUser);
        factory.setPassword(RabbitPassword);
    }

    /**
     * Converts the KeyToPressName into a XML-formatted instruction which presses that button
     *
     * @param RemoteName Name of the remote according to rabbitmq
     * @param ConfigToSend Key that must be pressed
     */
    private String convertToXmlInstruction(String RemoteName, String ConfigToSend){
        String RabbitWorkerId = "living-pi";

        String Message_To_Send;

        Message_To_Send = "<instruction" +
                " type=\"" + InstructionName + "\"" +
                " target=\"" + RabbitWorkerId + "\"" +
                " remote=\"" + RemoteName + "\"" +
                " config=\"" + ConfigToSend + "\"" +
                "/>";

        ////////////////////////
        return Message_To_Send;
        ////////////////////////
    }



    /**
     * Attempts to connect to the RabbitMQ server.
     */
    private void createRabbitChannel() {

        // Attempts to connect to the server as long as the connection and channel could not be
        // initialized
        while (connection == null && channel == null) {

            try {

                // Initializes connection and channel with the RabbitMQ server.
                connection = factory.newConnection();
                channel = connection.createChannel();

            } catch (IOException | TimeoutException e) {

                // Connection failed. Prints exception, resets parameters, and waits before retry.
                e.printStackTrace();

                connection = null;
                channel = null;

                try {

                    Thread.sleep(3000);

                } catch (InterruptedException e1) {

                    // Waiting phase was interrupted. Retry immediately
                    e1.printStackTrace();
                }
            }
        }
    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param RemoteName Name of the remote according to rabbitmq
     * @param ConfigToSend Key that must be pressed
     */
    void publishMessage(String RemoteName, String ConfigToSend) {

        final String MessageToSend = convertToXmlInstruction(RemoteName, ConfigToSend);

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                // Resets parameters if the channel is closed.
                if (channel != null && channel.isOpen()){

                    connection = null;
                    channel = null;

                }

                // Creates connexion with RabbitMQ server if it did not exist already.
                createRabbitChannel();

                // Sends message
                try {
                    System.out.println(MessageToSend);

                    channel.confirmSelect();
                    channel.basicPublish("ex", InstructionName, false, null, MessageToSend.getBytes());

                } catch (IOException e) {

                    System.out.println("Could not initiate connection.");
                    e.printStackTrace();

                }
            }
        });

        publishThread.start();

    }

}
