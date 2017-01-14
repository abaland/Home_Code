package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;

import java.io.IOException;
import java.util.HashMap;
import java.util.concurrent.TimeoutException;

import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;

public class tv_remote extends AppCompatActivity {

    private ConnectionFactory factory = new ConnectionFactory();
    private Connection connection;
    private Channel channel;
    private HashMap<String, String> ButtonToInstructionMapping = new HashMap<>();

    private String HostIp = "192.168.11.2";
    private String RabbitUser = "username";
    private String RabbitPassword = "password";
    private String RabbitWorkerId = "living-room";
    private String InstructionName = "remote_control";
    private String RemoteName = "tv";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tv_remote);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });

        ////////////////
        // Start added.
        ////////////////

        // Initializes the mapping between text on the buttons and the instruction to send
        ButtonToInstructionMapping.put("Power", "KEY_POWER");
        ButtonToInstructionMapping.put("Back", "KEY_BACK");
        ButtonToInstructionMapping.put("Mode", "KEY_MODE");
        ButtonToInstructionMapping.put("Up", "KEY_UP");
        ButtonToInstructionMapping.put("Left", "KEY_LEFT");
        ButtonToInstructionMapping.put("Ok", "KEY_OK");
        ButtonToInstructionMapping.put("Right", "KEY_RIGHT");
        ButtonToInstructionMapping.put("Bottom", "KEY_DOWN");
        ButtonToInstructionMapping.put("1", "KEY_NUMERIC_1");
        ButtonToInstructionMapping.put("2", "KEY_NUMERIC_2");
        ButtonToInstructionMapping.put("3", "KEY_NUMERIC_3");
        ButtonToInstructionMapping.put("4", "KEY_NUMERIC_4");
        ButtonToInstructionMapping.put("5", "KEY_NUMERIC_5");
        ButtonToInstructionMapping.put("6", "KEY_NUMERIC_6");
        ButtonToInstructionMapping.put("7", "KEY_NUMERIC_7");
        ButtonToInstructionMapping.put("8", "KEY_NUMERIC_8");
        ButtonToInstructionMapping.put("9", "KEY_NUMERIC_9");
        ButtonToInstructionMapping.put("Ch+", "KEY_CHANNELUP");
        ButtonToInstructionMapping.put("Vol+", "KEY_VOLUMEUP");
        ButtonToInstructionMapping.put("Ch-", "KEY_CHANNELDOWN");
        ButtonToInstructionMapping.put("Vol-", "KEY_VOLUMEDOWN");
        ButtonToInstructionMapping.put("Subs", "KEY_SUBTITLE");
        ButtonToInstructionMapping.put("Mute", "KEY_MUTE");

        // Initializes connectionFactory parameters, to start connexions with server
        factory.setHost(HostIp);
        factory.setUsername(RabbitUser);
        factory.setPassword(RabbitPassword);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_tv_remote, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }


    /**
     * Converts the KeyToPressName into a XML-formatted instruction which presses that button
     *
     * @param KeyToPress Name of the key in the remote that must be pressed.
     */
    private String convertToXmlInstruction(String KeyToPress){

        String Message_To_Send;

        Message_To_Send = "<instruction" +
                " type=\"" + InstructionName + "\"" +
                " target=\"" + RabbitWorkerId + "\"" +
                " remote=\"" + RemoteName + "\"" +
                " button=\"" + KeyToPress + "\"" +
                "/>";

        ////////////////////////
        return Message_To_Send;
        ////////////////////////
    }


    /**
     * Applies appropriate function when button on GUI is clicked.
     *
     * Uses text on button and mapping created to get more information about what should be sent.
     *
     * @param v Button clicked, as a View object.
     */
    void onClickFunction(View v){

        // Casts button clicked as a Button instance, and gets its text content.
        Button clickedButton = (Button) v;
        String ButtonText = clickedButton.getText().toString();

        System.out.println(ButtonText);
        String KeyToPress = ButtonToInstructionMapping.get(ButtonText);

        String MessageToSend = convertToXmlInstruction(KeyToPress);
        publishMessage(MessageToSend);

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
     * @param MessageToSend Message to send through RabbitMQ
     */
    private void publishMessage(final String MessageToSend) {

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
