import org.sikuli.script.App;
import org.sikuli.script.Screen;
import org.sikuli.script.Pattern;
import org.sikuli.script.FindFailed;
import org.sikuli.script.ImagePath;
import org.sikuli.script.Button;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import java.net.URI;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Sikuli Server - In-memory Sikuli execution service
 * 
 * This server receives commands from clients and executes Sikuli operations without restarting the JVM
 */
public class SikuliServer {
    private static final Logger logger = Logger.getLogger(SikuliServer.class.getName());
    private static final int DEFAULT_PORT = 5000;
    private final int port;
    private final ExecutorService executor;
    private final String scriptFolder;
    private boolean running = false;
    private ServerSocket serverSocket = null;

    public SikuliServer(int port, int threads, String scriptFolder) {
        this.port = port;
        this.executor = Executors.newFixedThreadPool(threads);
        this.scriptFolder = scriptFolder;
        
        // 設置Sikuli圖像路徑
        if (scriptFolder != null && !scriptFolder.isEmpty()) {
            try {
                ImagePath.add(scriptFolder);
                logger.info("已添加Sikuli圖像路徑: " + scriptFolder);
            } catch (Exception e) {
                logger.warning("添加圖像路徑時出錯: " + e.getMessage());
            }
        }
    }

    public void start() {
        running = true;
        try {
            serverSocket = new ServerSocket(port);
            logger.info("Sikuli服務器已啟動，監聽端口: " + port);
            logger.info("等待連接...");

            while (running) {
                try {
                    Socket clientSocket = serverSocket.accept();
                    logger.info("接受了新連接: " + clientSocket.getInetAddress());
                    executor.submit(new ClientHandler(clientSocket));
                } catch (IOException e) {
                    if (running) {
                        logger.log(Level.SEVERE, "接受連接時出錯", e);
                    }
                }
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, "啟動服務器時出錯", e);
        } finally {
            stop();
        }
    }

    public void stop() {
        running = false;
        if (serverSocket != null && !serverSocket.isClosed()) {
            try {
                serverSocket.close();
            } catch (IOException e) {
                logger.log(Level.WARNING, "關閉服務器套接字時出錯", e);
            }
        }
        executor.shutdown();
        logger.info("Sikuli服務器已停止");
    }

    private class ClientHandler implements Runnable {
        private final Socket clientSocket;

        public ClientHandler(Socket socket) {
            this.clientSocket = socket;
        }

        @Override
        public void run() {
            try (
                BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)
            ) {
                String inputLine = in.readLine();
                if (inputLine != null) {
                    logger.info("收到命令: " + inputLine);
                    
                    try {
                        // 解析命令
                        String[] args = inputLine.split("\\s+");
                        if (args.length > 0) {
                            String result = executeCommand(args);
                            out.println("OK: " + result);
                        } else {
                            out.println("ERROR: 空命令");
                        }
                    } catch (Exception e) {
                        logger.log(Level.SEVERE, "執行命令時出錯", e);
                        out.println("ERROR: " + e.getMessage());
                    }
                }
            } catch (IOException e) {
                logger.log(Level.SEVERE, "處理客戶端連接時出錯", e);
            } finally {
                try {
                    clientSocket.close();
                } catch (IOException e) {
                    logger.log(Level.WARNING, "關閉客戶端套接字時出錯", e);
                }
            }
        }

        private String executeCommand(String[] args) {
            try {
                logger.info("Executing command: " + Arrays.toString(args));
                
                // Get command parameters
                String topic = args[0];
                String action = args.length > 1 ? args[1] : "";
                
                // Execute Python script directly, which is more reliable
                return executePythonScript(args);
                
                /* Direct Sikuli API use is problematic in some environments
                // Create Screen object
                Screen screen = new Screen();
                
                // Execute different actions based on topic and action
                if (topic.equals("btn1")) {
                    if (action.equals("single")) {
                        return executeSingleClick(screen);
                    } else if (action.equals("double")) {
                        return executeDoubleClick(screen);
                    } else if (action.equals("long")) {
                        return executeLongPress(screen);
                    }
                }
                */
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Error executing Sikuli command", e);
                return "Execution error: " + e.getMessage();
            }
        }
        
        private String executeSingleClick(Screen screen) {
            try {
                // 此處添加具體的Sikuli操作
                // 例如：點擊屏幕上的某個按鈕
                screen.click(new Pattern(scriptFolder + "/button.png"));
                return "執行了單擊操作";
            } catch (FindFailed e) {
                return "找不到目標元素: " + e.getMessage();
            }
        }
        
        private String executeDoubleClick(Screen screen) {
            try {
                // 雙擊操作
                screen.doubleClick(new Pattern(scriptFolder + "/button.png"));
                return "執行了雙擊操作";
            } catch (FindFailed e) {
                return "找不到目標元素: " + e.getMessage();
            }
        }
        
        private String executeLongPress(Screen screen) {
            try {
                // 長按操作
                Pattern p = new Pattern(scriptFolder + "/button.png");
                screen.find(p);  // 首先找到位置
                screen.mouseDown(Button.LEFT);  // 按下左鍵
                Thread.sleep(1000); // 按住1秒
                screen.mouseUp(Button.LEFT);  // 釋放左鍵
                return "執行了長按操作";
            } catch (FindFailed | InterruptedException e) {
                return "執行長按操作出錯: " + e.getMessage();
            }
        }
        
        private String executePythonScript(String[] args) {
            try {
                // Execute Sikuli Python script
                String scriptPath = scriptFolder + "/execution.py";
                logger.info("Executing Python script: " + scriptPath + " " + Arrays.toString(args));
                
                // Create command to run the script using the Sikuli JAR
                List<String> cmd = new ArrayList<>();
                cmd.add("java");
                cmd.add("-jar");
                // Get the absolute path of the JAR file in the same directory as this class
                String jarPath = new File(SikuliServer.class.getProtectionDomain().getCodeSource().getLocation().toURI())+ "/sikulixapi-2.0.5-win.jar";
                logger.info("jarPath: " + jarPath);
                logger.info("jarPath: " + jarPath);
                logger.info("jarPath: " + jarPath);
                cmd.add(jarPath);
                cmd.add("-r");
                cmd.add(scriptFolder);
                cmd.add("--");
                
                // Add all arguments
                for (String arg : args) {
                    cmd.add(arg);
                }
                
                // Execute the process and capture output
                ProcessBuilder pb = new ProcessBuilder(cmd);
                pb.redirectErrorStream(true);
                Process process = pb.start();
                
                // Read the output
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                StringBuilder output = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                    logger.info("Script output: " + line);
                }
                
                // Wait for the process to complete
                int exitCode = process.waitFor();
                logger.info("Script execution completed with exit code: " + exitCode);
                
                return "Script executed, output: " + output.toString();
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Error executing Python script", e);
                return "Script execution error: " + e.getMessage();
            }
        }
    }

    public static void main(String[] args) {
        int port = DEFAULT_PORT;
        int threads = 4;
        String scriptFolder = "./execution.sikuli";
        
        // 解析命令行參數
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                logger.warning("無效的端口號，使用默認值: " + DEFAULT_PORT);
            }
        }
        
        if (args.length > 1) {
            scriptFolder = args[1];
        }
        
        if (args.length > 2) {
            try {
                threads = Integer.parseInt(args[2]);
            } catch (NumberFormatException e) {
                logger.warning("無效的線程數，使用默認值: 4");
            }
        }
        
        // 創建並啟動服務器
        SikuliServer server = new SikuliServer(port, threads, scriptFolder);
        
        // 添加關閉鉤子，確保服務器正常關閉
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("關閉服務器...");
            server.stop();
        }));
        
        server.start();
    }
}