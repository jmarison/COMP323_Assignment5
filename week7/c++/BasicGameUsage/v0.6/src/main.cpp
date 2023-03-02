/*
* basic game usage
* - main.cpp
* - v0.6
* - add basic audio usage
* - e.g. sprite jump event
*/

// work with string
#include <sstream>
// include sfml graphics
#include <SFML/Graphics.hpp>
// include sfml audio
#include <SFML/Audio.hpp>

// define namespace for current app
using namespace sf;

/* animate assets...
* - blocks
*/
// FN declaration
void updateBlocks(int seed);

const int NUM_BLOCKS = 6;
Sprite blocks[NUM_BLOCKS];
// player & block posn
// - left or right
enum class side { LEFT, RIGHT, NONE };
side blockPositions[NUM_BLOCKS];
/* END of animate assets */


// initial bootstrap for game
int main() {

	// audio buffer and sound objects
	SoundBuffer jumpBuffer;
	jumpBuffer.loadFromFile("../assets/audio/jump-short.wav");
	Sound jump;
	jump.setBuffer(jumpBuffer);

	/* extras */
	// define font file
	Font font;
	// load font from local file
	font.loadFromFile("../assets/fonts/Vera.ttf");

	// create video mode object
	VideoMode vm(1920, 1080);

	// create and open game window
	RenderWindow window(vm, "BasicGameUsage", Style::Fullscreen);

	// define a texture - holds graphic on GPU
	Texture textureBg;
	// load graphic on texture
	textureBg.loadFromFile("../assets/graphics/level-bg-basic1.png");	
	// create sprite
	Sprite spriteBg;
	// attach texture to sprite
	spriteBg.setTexture(textureBg);
	// set spriteBg to cover screen
	spriteBg.setPosition(0,0);	

	// create non-animated sprite object
	Texture textureBlock;
	textureBlock.loadFromFile("../assets/graphics/blue-vert-block.png");
	Sprite vertBlock;
	vertBlock.setTexture(textureBlock);
	vertBlock.setPosition(100,560);

	// create sprite for animate object
	Texture textureBall;
	textureBall.loadFromFile("../assets/graphics/beach-ball-orange.png");
	Sprite spriteBall;
	spriteBall.setTexture(textureBall);
	spriteBall.setPosition(300, 760);

	// define initial settings for spriteBall
	// - define initial motion
	bool ballActive = false;
	// - default speed for ball motion (f = float)
	float ballSpeed = 0.0f;

	// control time
	Clock clock;
	/* status bar for timer &c. */
	RectangleShape statusBar;
	float barStartWidth = 400;
	float barHeight = 80;
	statusBar.setSize(Vector2f(barStartWidth, barHeight));
	statusBar.setFillColor(Color::Blue);
	statusBar.setPosition((1920 / 2) - barStartWidth / 2, 20);

	// manage game timer
	Time totalTime;
	float timeRemaining = 6.0f;
	float barWidthPerSec = barStartWidth / timeRemaining;

	// record if game is active or paused
	bool paused = true;

	// draw some text to game window
	int score = 0;

	/* Text Objects & Fonts */
	// define text objects
	Text msgText;
	Text scoreText;

	// define string for text objects
	msgText.setString("Press Enter to Start...");
	scoreText.setString("Score = 0");

	// define font for text usage
	msgText.setFont(font);
	scoreText.setFont(font);

	// set size for font with text
	msgText.setCharacterSize(50);
	scoreText.setCharacterSize(50);

	// define colour for text
	msgText.setFillColor(Color::Black);
	scoreText.setFillColor(Color::Black);

	// position the text
	FloatRect textRect = msgText.getLocalBounds();
	
	// set origin for rendering text
	msgText.setOrigin(textRect.left +
		textRect.width / 2.0f,
		textRect.top + 
		textRect.height / 2.0f);

	msgText.setPosition(1920 / 2.0f, 1080 / 2.0f);

	scoreText.setPosition(20, 20);
	/* END of text & font */

	/* setup sprites &c. for animated blocks
	*/
	// prepare 6 blocks
	Texture textureBlockAnim;
	textureBlockAnim.loadFromFile("../assets/graphics/small_vert_block_green.png");
	// set texture for each block sprite
	for (int i = 0; i < NUM_BLOCKS; i++) {
		blocks[i].setTexture(textureBlockAnim);
		blocks[i].setPosition(-2000, -2000); // initially off screen
		// set sprite's origin to centre
		blocks[i].setOrigin(220, 20);
	}	
	
	// test blocks usage
	updateBlocks(1);
	updateBlocks(2);
	updateBlocks(3);
	updateBlocks(4);
	updateBlocks(5);

	/* player sprite object
	*/
	// prepare the player
	Texture texturePlayer;
	texturePlayer.loadFromFile("../assets/graphics/player-square.png");
	Sprite spritePlayer;
	spritePlayer.setTexture(texturePlayer);
	spritePlayer.setPosition(580, 780);
	// set default posn for player to left
	//side playerSide = side::LEFT;

	// set initial default - accept player input
	bool acceptInput = false;

	/* GAME LOOP */
	while (window.isOpen()) {
		/* 
		* handle player input
		*/

		Event event;
		// check for event
		while (window.pollEvent(event)) {
			// if event is key relased by user & game active
			if (event.type == Event::KeyReleased && !paused) {
				// update user input again
				acceptInput = true;
				if (event.key.code == Keyboard::Up) {
					spritePlayer.setPosition(spritePlayer.getPosition().x, spritePlayer.getPosition().y + 50);
				}
			}
		}

		if (Keyboard::isKeyPressed(Keyboard::Escape)) {
			window.close();
		}

		// start the game - check for Return keypress
		if (Keyboard::isKeyPressed(Keyboard::Return)) {
			// update game active state
			paused = false;
			// reset timer and game score
			score = 0;
			timeRemaining = 6;

			// update bool for player input - ready for use
			// - player can now move sprite in game window
			acceptInput = true;
		}

		// wrap player controls - checks bool for player input is true
		if (acceptInput) {
			
			// handle player input - right arrow key
			if (Keyboard::isKeyPressed(Keyboard::Right)) {
				// check game window boundary - right edge
				// - x value includes width of sprite obj
				if ( spritePlayer.getPosition().x > 2020 ) {
					// reset player posn to left edge of game window
					// start sprite obj outside of window boundary to avoid sprite jumping
					// - i.e. sprite smoothly scrolls onto window instead of automatically resetting to start of visible window
					spritePlayer.setPosition(-40, spritePlayer.getPosition().y);
				} else {
					// update player side
					//playerSide = side::RIGHT;
				// add time remaining whilst moving
				if ( score == 0 ) { // add check for 0 to avoid floating point exception
					timeRemaining += (2 / (score + 1)) + .01;
				} else {
					timeRemaining += (2 / score) + .01;
				}
					spritePlayer.setPosition(spritePlayer.getPosition().x + 5, spritePlayer.getPosition().y);
				}
			}	
			// handle player input - left arrow key
			if (Keyboard::isKeyPressed(Keyboard::Left)) {
				// check game window boundary - left edge
				if ( spritePlayer.getPosition().x < -40 ) {
					// reset player posn to right edge of game window
					spritePlayer.setPosition(2020, spritePlayer.getPosition().y);
				} else {
					//playerSide = side::LEFT;
				// add time remaining whilst moving
				if ( score == 0 ) { // add check for 0 to avoid floating point exception
					timeRemaining += (2 / (score + 1)) + .01;
				} else {
					timeRemaining += (2 / score) + .01;
				}
					spritePlayer.setPosition(spritePlayer.getPosition().x - 5, spritePlayer.getPosition().y);
				}
			}
			// handle player input - up arrow key
			if (Keyboard::isKeyPressed(Keyboard::Up)) {
				// play audio for jump
				jump.play();
				//playerSide = side::LEFT;
				// add time remaining whilst moving
				if ( score == 0 ) { // add check for 0 to avoid floating point exception
					timeRemaining += (2 / (score + 1)) + .01;
				} else {
					timeRemaining += (2 / score) + .01;
				}
				spritePlayer.setPosition(spritePlayer.getPosition().x, spritePlayer.getPosition().y - 50);
				acceptInput = false;
			}
				
					
		}
		
		/* 
		* update scene
		*/
		if (!paused) {
			// measure delta time - time between two updates
			Time dt = clock.restart();

			// subtract from time remaining
			timeRemaining -= dt.asSeconds();
			// size the status bar relative to timer
			statusBar.setSize(Vector2f(barWidthPerSec * timeRemaining, barHeight));
			
			// check when timer ends
			if (timeRemaining <= 0.1f) {
				// pause the game
				paused = true;
				
				// update message shown to player
				msgText.setString("That's enough time...");
				// reposition msgText bounding box relative to new text
				FloatRect textRect = msgText.getLocalBounds();
				msgText.setOrigin(textRect.left +
					textRect.width / 2.0f,
					textRect.top + 
					textRect.height / 2.0f);
				msgText.setPosition(1920 / 2.0f, 1080 / 2.0f);
			}

			// setup the ball
			if (!ballActive) {
			
				// how fast is the ball
				srand((int)time(0));
				ballSpeed = (rand() % 200) + 200;
				// how high is the ball
				srand((int)time(0) * 10);
				float height = (rand() % 500) + 500;
				spriteBall.setPosition(2000, height);

				ballActive = true;
			} else { // animate the ball
				spriteBall.setPosition(
					spriteBall.getPosition().x - (ballSpeed * dt.asSeconds()),
					spriteBall.getPosition().y);
			
				// check if ball has reached left window edge
				if (spriteBall.getPosition().x <  - 100) {
					// reset ball ready for next frame
					ballActive = false;
				}
			}

			// update score text
			std::stringstream ss;
			ss<< "Score = " << score;
			scoreText.setString(ss.str());

			// update block sprites
			for (int i = 0; i < NUM_BLOCKS; i++) {
				float height = i * 150;
				if (blockPositions[i] == side::LEFT) {
					// move sprite to left side
					blocks[i].setPosition(610, height);
					// flip sprite
					blocks[i].setRotation(180);
				} else if (blockPositions[i] == side::RIGHT) {
					// move sprite to right side
					blocks[i].setPosition(1330, height);
					// set sprite rotation to normal
					blocks[i].setRotation(0);
					
				} else {
					// hide the block
					blocks[i].setPosition(3000, height);
				}
			}

		}

		/* 
		* draw scene
		*/
		// clear last frame
		window.clear();

		// draw game scene
		window.draw(spriteBg);

		// draw small blocks
		for (int i = 0; i < NUM_BLOCKS; i++) {
			window.draw(blocks[i]);
		}

		// draw blue vertical block
		window.draw(vertBlock);
		// draw initial ball
		window.draw(spriteBall);

		// draw score
		window.draw(scoreText);

		// draw status bar
		window.draw(statusBar);

		// draw player
		window.draw(spritePlayer);
		
		if (paused) {
			// draw message text for game
			window.draw(msgText);
		}

		// render drawn game scene
		window.display();
		
	} /* END OF GAME LOOP */

	return 0;
}

// FN - update blocks with animation
void updateBlocks(int seed) {
	// move all blocks down one place
	for (int j = NUM_BLOCKS-1; j > 0; j--) {
		blockPositions[j] = blockPositions[j -1];
	}

	// spawn new block position 0
	// LEFT, RIGHT, or NONE
	srand((int)time(0)+seed);
	int r = (rand() % 5);

	switch (r) {
		case 0:
			blockPositions[0]  = side::LEFT;
			break;
		case 1:
			blockPositions[0] = side::RIGHT;
			break;
		default:
			blockPositions[0] = side::NONE;
			break;	
	}
}


