AsyncHelper helper = new AsyncHelper();

Console.WriteLine("Please wait");

string result = await helper.GetMessageAsync();

Console.WriteLine(result);