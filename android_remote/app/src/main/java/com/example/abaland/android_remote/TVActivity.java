package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;

import java.util.HashMap;


public class TVActivity extends AppCompatActivity {

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
        ButtonToInstructionMapping.put("Vol+", "KEY_VOLUMEUP");
        ButtonToInstructionMapping.put("Vol-", "KEY_VOLUMEDOWN");

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
        rabbit_manager.publishMessage(RemoteName, KeyToPress, TVActivity.this);

    }

}
