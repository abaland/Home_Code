package com.example.abaland.android_remote;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;

import android.support.v7.app.AppCompatActivity;

import java.io.IOException;
import java.util.concurrent.TimeoutException;


class Rabbit_Manager {

    private ConnectionFactory factory = new ConnectionFactory();
    private Connection connection;
    private Channel channel;


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
     * Attempts to connect to the RabbitMQ server.
     *
     * @param context Activity that called the publishMessage function
     * @return whether creation of channel was successfull or not.
     */
    private boolean createRabbitChannel(AppCompatActivity context) {

        // Attempts to connect to the server (only one attempt)
        try {

            if (channel == null || connection == null) {

                // Initializes connection and channel with the RabbitMQ server.
                connection = factory.newConnection();
                channel = connection.createChannel();

            }

            // Succeeded : return true.
            /////////////
            return true;
            /////////////

        } catch (IOException | TimeoutException e) {

            // Connection failed. Prints exception, resets parameters, and returns failure status.
            new CustomLogger("Rabbit", "Could not create Rabbit channel : " + e.getMessage(),
                    context, true);

            connection = null;
            channel = null;

            //////////////
            return false;
            //////////////

        }

    }


    /**
     * Checks whether the channel is still open and resets paraeters otherwise
     */
    private void checkChannelParameters() {

        // Resets parameters if the channel is closed.
        if (channel != null && !channel.isOpen()){

            connection = null;
            channel = null;

        }

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    private void publishMessage(final String instructionName, final String messageToSend,
                        final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.confirmSelect();
                channel.basicPublish("ex", instructionName, false, null,
                        messageToSend.getBytes());

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param callback Consumer object that contains the callback function to be called
     * @param context Activity that called the publishMessage function
     */
    private String declareTemporaryQueue(final Consumer callback, final AppCompatActivity context) {

        String queueName = null;

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                queueName = channel.queueDeclare().getQueue();
                channel.basicConsume(queueName, false, callback);
                System.out.println("Temporary queue created");

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

        return queueName;

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param queueName Name of queue to be removed
     * @param context Activity that called the publishMessage function
     */
    private  void remoteTemporaryQueue(final String queueName, final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.queueDelete(queueName);

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Declares a temporary queue messages from the server and declares the feed from this queue
     *
     * @param deliveryTag ??
     * @param context Activity that called the publishMessage function
     */
    void acknowledgeMessage(final long deliveryTag, final AppCompatActivity context) {

        // Resets parameters if the channel is closed.
        checkChannelParameters();

        // Creates connexion with RabbitMQ server if it did not exist already.
        if (createRabbitChannel(context)) {

            // Sends message.
            try {

                channel.basicAck(deliveryTag, false);

            } catch (IOException e) {

                // Failed to publish message. Log error and stops
                new CustomLogger("Rabbit", "Could not send rabbitmq message. Giving up : " +
                        e.getMessage(), context, true);

            }

        }

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    void askWorker(final String instructionName, final String messageToSend,
                   final AppCompatActivity context) {

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                publishMessage(instructionName, messageToSend, context);

            }

        });

        publishThread.start();

    }


    /**
     * Sends message to workers through RabbitMQ.
     *
     * @param messageToSend Message to send through RabbitMQ
     * @param context Activity that called the publishMessage function
     */
    void askWorker(final String instructionName, final String messageToSend,
                   final AppCompatActivity context, final Consumer callback) {

        Thread publishThread = new Thread(new Runnable() {

            @Override
            public void run() {

                String queueName = declareTemporaryQueue(callback, context);
                publishMessage(instructionName, messageToSend, context);

                remoteTemporaryQueue(queueName, context);

            }

        });

        publishThread.start();

    }


}
