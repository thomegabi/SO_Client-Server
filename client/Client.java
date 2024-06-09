import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.Arrays;

public class Client {
    private static Socket socket;
    private static BufferedReader reader;
    private static PrintWriter writer;
    private static final String[] MESSAGES = {"list_dir", "sys_info", "mouse_control"};

    public static void main(String[] args) {
        try {
            socket = new Socket("localhost", 9999);
            reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            writer = new PrintWriter(socket.getOutputStream(), true);

            Scanner scanner = new Scanner(System.in);

            System.out.println("Conexão com o servidor estabelecida com sucesso!");

            Thread sendMessage = new Thread(() -> {
                try {
                    while (!Thread.currentThread().isInterrupted()) {
                        System.out.println("Comandos possíveis: " + String.join(", ", MESSAGES));
                        System.out.println("Digite o comando:");

                        String action = scanner.nextLine().trim();
                        if (isValidMessage(action)) {
                            String command = "";
                            if (!action.equals("sys_info")) {
                                if (action.equals("mouse_control")) {
                                    System.out.println("Parâmetros possíveis: limit, invert, punch, lock");
                                    System.out.println("Digite o comando do mouse:");
                                    command = scanner.nextLine().trim();
                                    if (command.equals("limit")) {
                                        System.out.println("Digite o tamanho da área ao redor:");
                                        int aroundSize = Integer.parseInt(scanner.nextLine().trim());
                                        while (aroundSize <= 0) {
                                            System.out.println("O tamanho da área ao redor deve ser maior que zero. Digite novamente:");
                                            aroundSize = Integer.parseInt(scanner.nextLine().trim());
                                        }

                                        System.out.println("Digite a duração em segundos:");
                                        int duration = Integer.parseInt(scanner.nextLine().trim());
                                        while (duration <= 0) {
                                            System.out.println("A duração deve ser maior que zero. Digite novamente:");
                                            duration = Integer.parseInt(scanner.nextLine().trim());
                                        }
                                        command = command + "|{" + "\"around_size\":" + aroundSize + ",\"duration\":" + duration + "}";
                                    } else if (command.equals("lock")) {
                                        command = "lock";
                                    } else if(command.equals("invert")){
                                        command = "invert";
                                    } else if(command.equals("punch")){
                                        command = "punch";
                                    }
                                    
                                } else if (action.equals("execute")) {
                                    System.out.println("Digite o comando do sistema para executar:");
                                    command = scanner.nextLine().trim();
                                } else if (action.equals("list_dir")) {
                                    System.out.println("Digite o caminho do diretório (ou deixe em branco para o diretório padrão):");
                                    command = scanner.nextLine().trim();
                                } else {
                                    System.out.println("Digite o parâmetro do comando:");
                                    command = scanner.nextLine().trim();
                                }
                            }
                            String message = action + (command.isEmpty() ? "" : "|" + command);
                            writer.println(message);
                        } else {
                            System.out.println("Mensagem inválida. Tente novamente.");
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    scanner.close();
                    writer.close();
                }
            });

            Thread readMessage = new Thread(() -> {
                try {
                    while (true) {
                        String message = reader.readLine();
                        if (message == null) {
                            System.out.println("Recebido null, terminando leitura.");
                            break;
                        }
                        System.out.println("Servidor: " + message);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });


            sendMessage.start();
            readMessage.start();

            sendMessage.join();
            readMessage.join();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        } finally {
            try {
                if (socket != null && !socket.isClosed()) {
                    socket.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private static boolean isValidMessage(String message) {
        return Arrays.asList(MESSAGES).contains(message);
    }
}
