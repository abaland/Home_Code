package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;

import java.util.HashMap;


public class MainActivity extends AppCompatActivity {

    private Toolbar toolbar;
    private HashMap<String, String> ButtonToInstructionMapping = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

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

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
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
     * Applies appropriate function when button on GUI is clicked.
     *
     * Uses text on button and mapping created to get more information about what should be sent.
     *
     * @param v Button clicked, as a View object.
     */
    void onClickFunction(View v){

        String RemoteName = "tv";

        // Casts button clicked as a Button instance, and gets its text content.
        Button clickedButton = (Button) v;
        String ButtonText = clickedButton.getText().toString();

        System.out.println(ButtonText);
        String KeyToPress = ButtonToInstructionMapping.get(ButtonText);

        Rabbit_Manager rabbit_manager = new Rabbit_Manager();
        rabbit_manager.publishMessage(RemoteName, KeyToPress);

    }

}
