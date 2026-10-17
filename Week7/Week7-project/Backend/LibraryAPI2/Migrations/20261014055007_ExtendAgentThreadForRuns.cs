using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace LibraryAPI.Migrations
{
    /// <inheritdoc />
    public partial class ExtendAgentThreadForRuns : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "AgentThreads",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AddColumn<string>(
                name: "ErrorCode",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ErrorMessage",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "FinalAnswer",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsCancelled",
                table: "AgentThreads",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "LastApprovalDecision",
                table: "AgentThreads",
                type: "bit",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PendingApprovalJson",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Status",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<DateTime>(
                name: "UpdatedAt",
                table: "AgentThreads",
                type: "datetime2",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

            migrationBuilder.AddColumn<string>(
                name: "UserMessage",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_AgentThreads_UserId",
                table: "AgentThreads",
                column: "UserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_AgentThreads_UserId",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "ErrorCode",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "ErrorMessage",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "FinalAnswer",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "IsCancelled",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "LastApprovalDecision",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "PendingApprovalJson",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "Status",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "UpdatedAt",
                table: "AgentThreads");

            migrationBuilder.DropColumn(
                name: "UserMessage",
                table: "AgentThreads");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "AgentThreads",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");
        }
    }
}
