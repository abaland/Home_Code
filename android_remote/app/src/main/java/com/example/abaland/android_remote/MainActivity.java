package com.example.abaland.android_remote;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.AppCompatTextView;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Spinner;

import java.util.HashMap;


public class MainActivity extends AppCompatActivity {

    Rabbit_Manager rabbitManager;

    private int currentLayoutId;


    private void setupRemoteSpinner() {

        Spinner remoteSpinner = (Spinner) this.findViewById(R.id.remoteSpinner);

        final HashMap<String, Integer> remoteToLayoutMapping = new HashMap<>();

        // Initializes the mapping between text on the buttons and the instruction to send
        remoteToLayoutMapping.put("Aircon", R.id.aircon_layout);
        remoteToLayoutMapping.put("TV", R.id.tv_layout);
        remoteToLayoutMapping.put("Lights", R.id.lights_layout);

        // Adds listener for the fan speed spinner
        remoteSpinner.setOnItemSelectedListener(new Spinner.OnItemSelectedListener() {

            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView,
                                       int position, long id) {

                String selectedRemote = ((AppCompatTextView) selectedItemView).getText().toString();

                findViewById(currentLayoutId).setVisibility(View.GONE);
                currentLayoutId = remoteToLayoutMapping.get(selectedRemote);
                findViewById(currentLayoutId).setVisibility(View.VISIBLE);

            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {}

        });
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        ///////////////
        // Start added
        ///////////////

        // Creates initial rabbitmq connection manager instance
        rabbitManager = new Rabbit_Manager();

        // Set up aircon remote control interface (currently invisible)
        AirconControls airconControls = new AirconControls(this);
        airconControls.initialize();

        // Set up tv remote control interface (currently invisible)
        TVControls tvControls = new TVControls(this);
        tvControls.initialize();

        // Set up tv remote control interface (currently invisible)
        LightsControls lightControls = new LightsControls(this);
        lightControls.initialize();

        // Adds listener to remote spinner to choose switch between interfaces
        setupRemoteSpinner();

        // Makes aircon remote control interface visisble
        currentLayoutId = R.id.tv_layout;
        findViewById(currentLayoutId).setVisibility(View.VISIBLE);

    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu; this adds items to the action bar if it is present.
        // Logs message in app log.
        getMenuInflater().inflate(R.menu.menu_main, menu);

        /////////////
        return true;
        /////////////

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

}
